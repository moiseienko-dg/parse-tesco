from scrapy.exporters import JsonItemExporter


class TescoPipeline:

    def open_spider(self, spider):
        self.file = open('item.json', 'wb')
        self.exporter = JsonItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item