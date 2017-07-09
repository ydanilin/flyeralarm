#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy


''' We expect structure like this as output; feel free to compare that to the
page where it was scraped: https://www.saxoprint.co.uk/shop/folded-leaflets-48h

{
  "name": "48h Folded Leaflets",
  "caption": "48h Folded Leaflets",
  "thumbnail_file": [
    {
      "checksum": "e72c57cc5fb87f4854b3c71015272a03",
      "path": "full/f7eb988ed473c6d4836c3584f2e269f1267a4064.jpg",
      "url": "https://www.saxoprint.co.uk/folded-leaflets-printing.jpg"
    }
  ],
  "URL": "https://www.saxoprint.co.uk/shop/folded-leaflets-48h",
  "thumbnail_url": [
    "/Librarys/global/sxp/en_GB/shop/product/folded-leaflets-printing.jpg"
  ],
  "data": "599",
  "parameters": [
    {
      "name": "Print run",
      "data": "quantity",
      "supplier_product": "48h Folded Leaflets",
      "values": [
        {
          "name": "3,000",
          "supplier_parameter": "Print run",
          "data": "3,000",
          "supplier_product": "48h Folded Leaflets"
        },
        {
          "name": "2,500",
          "supplier_parameter": "Print run",
          "data": "2,500",
          "supplier_product": "48h Folded Leaflets"
        },
        {
          "name": "1,000",
          "supplier_parameter": "Print run",
          "data": "1,000",
          "supplier_product": "48h Folded Leaflets"
        }
        // skipped
      ]
    },
    {
      "name": "Finished size",
      "data": "TrimmedSize",
      "supplier_product": "48h Folded Leaflets",
      "values": [
        {
          "name": "A4 (297 x 210 mm) landscape",
          "supplier_parameter": "Finished size",
          "data": "49",
          "supplier_product": "48h Folded Leaflets"
        },
        {
          "name": "210 x 210 mm",
          "supplier_parameter": "Finished size",
          "data": "64",
          "supplier_product": "48h Folded Leaflets"
        }
        // skipped
      ]
    },
    {
      "name": "Number of sides/pages",
      "data": "Page",
      "supplier_product": "48h Folded Leaflets",
      "values": [
        {
          "name": "4 sides",
          "supplier_parameter": "Number of sides/pages",
          "data": "122",
          "supplier_product": "48h Folded Leaflets"
        },
        {
          "name": "6 sides",
          "supplier_parameter": "Number of sides/pages",
          "key": "default",
          "data": "123",
          "supplier_product": "48h Folded Leaflets"
        }
      ]
    },
    {
      "name": "Colour mode",
      "data": "Color",
      "supplier_product": "48h Folded Leaflets",
      "values": [
        {
          "name": "4/4-coloured euroscale",
          "supplier_parameter": "Colour mode",
          "key": "default",
          "data": "78",
          "supplier_product": "48h Folded Leaflets"
        }
      ]
    },
    {
      "name": "Material",
      "data": "Paper",
      "supplier_product": "48h Folded Leaflets",
      "values": [
        {
          "name": "250gsm gloss finish",
          "supplier_parameter": "Material",
          "data": "101",
          "supplier_product": "48h Folded Leaflets"
        },
        {
          "name": "300gsm gloss finish",
          "supplier_parameter": "Material",
          "data": "103",
          "supplier_product": "48h Folded Leaflets"
        }
        // skipped
      ]
    }
    // rest of parameter skipped
  ]
}
'''


class SupplierProductItem(scrapy.Item):
    name = scrapy.Field()
    caption = scrapy.Field()
    URL = scrapy.Field()
    supplier = scrapy.Field()
    ''' data is an arbitrary supplier-specific data used to identify this
    product within supplier site when e.g. corresponding different
    translations'''
    data = scrapy.Field()
    thumbnail_url = scrapy.Field()
    thumbnail_file = scrapy.Field()

    def __repr__(self):
        return '<Product: ' + self.get('name', '(unknown)') + ' on ' + \
            str(self.get('supplier', '(unknown supplier)')) + '>'


class SupplierParameterItem(scrapy.Item):
    name = scrapy.Field()
    supplier = scrapy.Field()
    supplier_product = scrapy.Field()
    default_value = scrapy.Field()
    min_value = scrapy.Field()
    max_value = scrapy.Field()
    ''' data is an arbitrary supplier-specific data used to identify this
    parameter within supplier site when e.g. doing price scraping '''
    data = scrapy.Field()

    def __repr__(self):
        return '<Parameter: ' + self.get('name', '(unknown)') + ' of ' + \
            str(self.get('supplier_product', '(unknown)')) + ' on ' + \
            str(self.get('supplier', '(unknown supplier)')) + '>'


class SupplierValueItem(scrapy.Item):
    name = scrapy.Field()
    supplier_parameter = scrapy.Field()
    supplier = scrapy.Field()
    supplier_product = scrapy.Field()
    ''' data is an arbitrary supplier-specific data used to identify this value
     within supplier site when e.g. doing price scraping '''
    data = scrapy.Field()

    key = scrapy.Field()  # default/min/max

    def __repr__(self):
        return '<Value: ' + self.get('name', '(unknown)') + '>'
