-- NOTE : put this file where Splash can find it; see http://splash.readthedocs.io/en/stable/scripting-libs.html#setting-up
local utils = {}

local Splash = require("splash")


function utils.contains(table, element)
    for _, value in pairs(table) do
        if value == element then
            return true
        end
    end
    return false
end

function utils.split(self, sep)
   local sep, fields = sep or " ", {}
   local pattern = string.format("([^%s]+)", sep)
   string.gsub(self, pattern, function(c) fields[#fields+1] = c end)
   return fields
end

function utils.trim(s)
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end

function Splash:find_element_by_xpath(xpath)
    return self:evaljs(string.format(
        "document.evaluate(%q, document, null, XPathResult.ANY_TYPE, null).iterateNext()", xpath))
end

function Splash:wait_for_js(js, ...)
    return self:wait_for_resume(string.format([[
        function main(splash) {
            var interval = setInterval(function() {
                if(%s)
                {
                    clearInterval(interval);
                    splash.resume();
                }
            }, 100);
        }
    ]], js:format(...)))
end

function Splash:wait_for_js_ex(js, timeout)
    return self:wait_for_resume(string.format([[
        function main(splash) {
            var interval = setInterval(function() {
                if(%s)
                {
                    clearInterval(interval);
                    splash.resume();
                }
            }, 100);
        }
    ]], js), timeout)
end

function Splash:wait_for_page_load(time)
    self:wait(time or 0.1)
    assert(self:wait_for_js(
        "document.readyState == 'complete' && $.active == 0 && !$('.loading-indicator').length && !$('#pr_ajax_wait').is(':visible')"))
end

function Splash:runjs_ex(js, ...)
    local ok, err = self:runjs(js:format(...))
    return ok, err and err.message or ''
end

function Splash:start(time)
    self.images_enabled = false
    self:set_viewport_size(1366, 768)
    self:init_cookies(self.args.cookies)
    local ok, reason = self:go{
        self.args.url,
        headers=self.args.headers,
        http_method=self.args.http_method,
        body=self.args.body,
    }
    if not ok and reason ~= "network301" then  -- 301 error appears to be glitch caused by adblock rules
        self:set_result_status_code(502)
        return false
    end
    self:wait_for_page_load(time or 1)
    return true
end

return utils
