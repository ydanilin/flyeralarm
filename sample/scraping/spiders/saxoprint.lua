local json = require("json")
local treat = require("treat")
local utils = require("utils")


function select_value(splash, parameter, value)
    parameter_id = parameter.fields.data
    value_id = value.fields.data
    if parameter.fields.min or parameter.fields.max then
        assert(splash:runjs_ex("document.getElementById(%q).value=%s; GetFileUrls();", parameter_id, value_id))
        return 1
    end

    local list_path = ""
    local values_path = ""
    local value_path = ""

    if parameter_id == "quantity" then
        list_path = "//div[@id='main']//div[@id='ddltext']"
        values_path = "//div[@id='main']//div[@id='ddlcontent']"
        value_path = values_path .. string.format("//li[.=%q]", value_id)
    else
        list_path = string.format("//div[@id='main']//ul[@id=%q]", parameter_id)
        values_path = list_path .. "//ul[@class='elements']"
        value_path = list_path .. string.format("//li[@value=%q]", value_id)
    end

    local list = splash:find_element_by_xpath(list_path)
    if not list then return 0 end
    list:mouse_click()
    splash:wait_for_page_load()
    if not splash:wait_for_js_ex(string.format(
            "document.evaluate(%q, document, null, XPathResult.ANY_TYPE, null).iterateNext().offsetParent !== null",
            values_path), 1) then
        -- NOTE: most probably it's unclickable due to value dependencies.
        -- NOTE: there is issue with value dependencies and value names e.g. when number of sides is 1, colour modes are 1/0,2/0 etc but when number of sides is 2, they become 1/1,2/2, i.e. different names, but same data IDs actually. This is covered for number of sides / colour mode case described above, but that might be not enough.
        local current = splash:find_element_by_xpath(list_path .. "//li[@class='current']")
        if not current or not current.attributes then return 0 end
        if current.attributes.value == value_id then return 1 else return 0 end
    end

    local element = splash:find_element_by_xpath(value_path)
    if not element or not element.node then return 0 end
    element:mouse_click()
    splash:wait_for_page_load()
    if parameter_id == "quantity" then
        return 1
    else
        if splash:find_element_by_xpath(value_path).attributes.class == "current" then return 1 else return 0 end
    end
end

function scrape_common_parameter(splash, item, class)
    if not item:querySelector("label") then return nil end
    local result = {
        name=item:querySelector("label"):text(),
        data=class,
        values={}
    }
    for _, choice in pairs(item:querySelectorAll("li")) do
        if choice.textContent and choice.textContent ~= "" and choice:text() ~= "null" then
            if utils.contains(choice.parentElement.classList, "elements") then
                local value = {name=choice:text(), data=choice:getAttribute("value")}
                if utils.contains(choice.classList, "selected") and not result["values"]["default"] then
                    result["values"]["default"] = value
                else
                    table.insert(result["values"], value)
                end
            end
        end
    end
    return result
end

function scrape_limited_parameter(splash, item)
    local input = item:querySelector("input.custominput")
    if not input then return nil end
    local result = {
        name=item:querySelector("div.inputlabel"):text(),
        data=input.id,
        values={}
    }
    local default = input:getAttribute("data-default")
    local min = input:getAttribute("data-min")
    local max = input:getAttribute("data-max")
    if default then result["values"]["default"] = {name=default, data=default} end
    if min then result["values"]["min"] = {name=min, data=min} end
    if max then result["values"]["max"] = {name=max, data=max} end
    return result
end

function scrape_quantity(splash, item)
    local result = {
        name=item:querySelector("div.inputlabel"):text(),
        data="quantity",
        values={}
    }
    for _, choice in pairs(item:querySelectorAll("li")) do
        table.insert(result["values"], {name=choice:text(), data=choice:text()})
    end
    local default = item:querySelector("div#ddltext"):text()
    result["values"]["default"] = {name=default, data=default}
    return result
end

function scrape_parameter(splash, item)
    if not item then return nil end
    local classes = item.classList
    local class = ""
    if next(classes) then class = classes[1] end
    if item.id == "quantity" then
        return scrape_quantity(splash, item)
    end
    if utils.contains(classes, "custominputcontainer") then
        return scrape_limited_parameter(splash, item)
    end
    if class:sub(1, 1):upper() == class:sub(1, 1) and class ~= "VariantOnPackage" then
        return scrape_common_parameter(splash, item, class)
    end
end

function scrape_parameters(splash)
    local result = {}
    local main = splash:select("div#main")
    for _, item in pairs(main:querySelectorAll("div")) do
        local parameter = scrape_parameter(splash, item)
        if parameter then
            result[#result+1] = parameter
            -- HACK: vary "Number of sides/pages" parameter, so that we get all possible colour modes
            if parameter.name == "Seitenanzahl" or parameter.name == "Number of sides/pages" then
                local one_side = nil
                for _, value in pairs(parameter.values) do
                    if value.name:find("1") then one_side = value.data end
                end
                if one_side then
                    select_value(splash, {fields={data=parameter.data}}, {fields={data=one_side}})
                    splash:wait_for_page_load()
                    parameter = scrape_parameter(splash, splash:select("div#main div.Color"))
                    if parameter then result[#result+1] = parameter end
                end
            end
        end
    end
    return result
end

function scrape_product(splash)
    if not splash:start() then return "" end

    local is_product_group = false
    if not splash:select("div#error") then is_product_group = true end
    local result = {html=splash:html(), cookies=splash:get_cookies(), is_product_group=is_product_group}
    if is_product_group then
        if splash:select("div.slider") then result["is_slider"] = true end
        if splash:select("ul.offergrid") then result["is_offergrid"] = true end
        if #splash:select_all("div.cb") > 3 then result["is_adjustable_group"] = true end
        return result
    end

    local product = {}
    product["URL"] = splash.args.url

    local data_tag = splash:select("div#ProductGroupHf")
    if not data_tag then return result end
    product["data"] = data_tag:text()

    local shopheadline = splash:select("div.shopheadline")
    if shopheadline then
        product["name"] = table.concat(utils.split(shopheadline:querySelector("h1"):text()), " ")
    else
        if splash.args.name then
            product["name"] = splash.args.name
        else
            return result
        end
    end
    product["caption"] = splash.args.headline
    if product["caption"] == "" or product["caption"]:find("Dimensions") or product["caption"]:find("Maße") then
        local sub = splash:select("div.shopsub")
        if sub then product["caption"] = table.concat(utils.split(sub:text()), " ") end
    end

    local preview = splash:select("div#productpreview")
    if not preview then preview = splash:select("div.fsg-img") end
    local thumbnail = nil
    if preview then thumbnail = preview:querySelector("img") end
    product["thumbnail_url"] = {""}
    if thumbnail then product["thumbnail_url"] = {thumbnail:getAttribute("src")} end
    treat.as_array(product["thumbnail_url"])

    product["parameters"] = scrape_parameters(splash)
    treat.as_array(product["parameters"])

    return {
        cookies=splash:get_cookies(),
        --png=splash:png(),
        --har=splash:har(),
        product = product
    }
end

function main(splash)
    if not splash:start() then return "" end
    return {
        html=splash:html(),
        cookies=splash:get_cookies()
    }
end
