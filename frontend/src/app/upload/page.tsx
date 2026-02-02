"use client";

import { useState } from "react";
import { UploadLayout } from "@/components/upload";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  AlertCircle,
  Link as LinkIcon,
  Search,
  Database,
  FileSpreadsheet,
  Table2,
  Image,
  FileText,
  Package,
  Truck,
  Play,
  ChevronDown,
  ChevronUp,
  Loader2,
  Tag,
  Info,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DataSource {
  id: string;
  name: string;
  type: "dingtalk" | "feishu" | "excel";
  description: string;
}

interface Template {
  id: string;
  name: string;
  category: string;
  fields: string[];
}

interface SKUItem {
  id: string;
  name: string;
  image: string;
  price: number;
  originalPrice?: number;
  stock?: number;
}

interface ParamItem {
  name: string;
  value: string;
}

interface CollectedProduct {
  title: string;
  price: string;
  originalPrice?: string;
  video: boolean;
  mainImages: string[];
  detailImages: string[];
  skus: SKUItem[];
  params: ParamItem[];
}

// 模拟数据
const configuredDataSources: DataSource[] = [
  { id: "ds1", name: "商品主数据表", type: "dingtalk", description: "商家编码、有机编码、厂家信息" },
  { id: "ds2", name: "有机认证数据", type: "feishu", description: "有机证书、认证编号" },
  { id: "ds3", name: "价格库存表.xlsx", type: "excel", description: "SKU价格、库存" },
];

const availableTemplates: Template[] = [
  { id: "t1", name: "特色米/面粉模板", category: "粮油调味/米/面粉/杂粮", fields: ["发货地", "物流模板", "售后承诺", "厂家信息"] },
  { id: "t2", name: "坚果炒货模板", category: "零食/坚果/特产", fields: ["发货地", "物流模板", "售后承诺"] },
];

const dataSourceIcons = {
  dingtalk: <Table2 className="h-4 w-4" />,
  feishu: <FileSpreadsheet className="h-4 w-4" />,
  excel: <FileSpreadsheet className="h-4 w-4" />,
};

export default function UploadStep1() {
  const [url, setUrl] = useState("");
  const [isCollecting, setIsCollecting] = useState(false);
  const [collectedProduct, setCollectedProduct] = useState<CollectedProduct | null>(null);

  // 数据源状态
  const [selectedDataSource, setSelectedDataSource] = useState<string | null>(null);
  const [isMatching, setIsMatching] = useState(false);
  const [matchedFields, setMatchedFields] = useState<{ name: string; value: string; source: string }[] | null>(null);

  // 模板状态
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [templatePreview, setTemplatePreview] = useState<{ name: string; value: string }[] | null>(null);

  // 展开状态
  const [expandedSections, setExpandedSections] = useState({
    skus: true,
    params: true,
    detailImages: false,
  });

  const handleCollect = () => {
    if (!url) return;
    setIsCollecting(true);
    setCollectedProduct(null);
    setSelectedDataSource(null);
    setMatchedFields(null);
    setSelectedTemplate(null);
    setTemplatePreview(null);

    setTimeout(() => {
      setIsCollecting(false);
      setCollectedProduct({
        title: "九月的诗有机黑芝麻730g*1罐生熟可选即食免洗炒熟馅料农家新货",
        price: "¥49.31",
        originalPrice: "¥59.9",
        video: true,
        mainImages: ["1", "2", "3", "4", "5"],
        detailImages: ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"],
        skus: [
          { id: "1", name: "(生)有机黑芝麻730g*1罐", image: "", price: 49.31, originalPrice: 59.9 },
          { id: "2", name: "(熟)有机黑芝麻600g*1罐", image: "", price: 45.80, originalPrice: 55.0 },
          { id: "3", name: "有机生黑芝麻730g+有机黑豆800g", image: "", price: 79.90, originalPrice: 99.0 },
        ],
        params: [
          { name: "产地", value: "中国大陆" },
          { name: "品牌", value: "九月的诗" },
          { name: "生产日期", value: "2025年08月23日 至 2025年11月17日" },
          { name: "系列", value: "有机" },
          { name: "规格", value: "730g" },
          { name: "货号", value: "黑芝麻" },
          { name: "包装方式", value: "罐装" },
          { name: "品名", value: "有机黑芝麻" },
          { name: "口味", value: "(生)有机黑芝麻730g*1罐 (熟)有机黑芝麻600g*1罐 有机生黑芝麻730g+有机黑豆800g" },
          { name: "适用场景", value: "家用" },
          { name: "单件净含量", value: "730g" },
          { name: "城市", value: "滨州市" },
          { name: "省份", value: "山东省" },
          { name: "包装规格", value: "1罐" },
          { name: "生产许可证", value: "SC10237162300022" },
          { name: "产品标准号", value: "GB/T11761" },
          { name: "厂名", value: "山东丰香园食品股份有限公司" },
          { name: "厂址", value: "山东省滨州市无棣县海丰十一路168号" },
          { name: "厂家联系方式", value: "见包装" },
          { name: "配料表", value: "有机黑芝麻" },
          { name: "储藏方法", value: "阴凉干燥通风处密闭保存" },
          { name: "保质期", value: "365天" },
        ],
      });
    }, 1500);
  };

  const handleMatchDataSource = () => {
    if (!selectedDataSource) return;
    setIsMatching(true);
    setTimeout(() => {
      setIsMatching(false);
      setMatchedFields([
        { name: "商家编码", value: "HZM-600G-S", source: "数据源" },
        { name: "有机编码", value: "2490P1800146", source: "数据源" },
        { name: "条形码", value: "6901234567890", source: "数据源" },
        { name: "有机证书", value: "已关联", source: "数据源" },
      ]);
    }, 800);
  };

  const handleSelectTemplate = (templateId: string) => {
    setSelectedTemplate(templateId);
    setTemplatePreview([
      { name: "发货地", value: "浙江杭州" },
      { name: "发货时效", value: "24小时内发货" },
      { name: "物流模板", value: "包邮模板A" },
      { name: "退换货", value: "7天无理由退换" },
      { name: "运费险", value: "赠送运费险" },
    ]);
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const canProceed = collectedProduct !== null;

  return (
    <UploadLayout
      step={1}
      title="采集商品"
      nextHref={canProceed ? "/upload/step2" : undefined}
      nextDisabled={!canProceed}
    >
      <div className="space-y-6">
        {/* ========== 区域1: 采集 ========== */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-orange-500 text-white text-xs font-bold">
              1
            </div>
            <h2 className="font-semibold text-gray-800">输入商品链接</h2>
          </div>

          <div className="flex gap-3">
            <div className="flex-1 relative">
              <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="https://item.taobao.com/item.htm?id=xxx"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="pl-11 h-12 rounded-xl border-gray-200 focus:border-orange-300 focus:ring-orange-200"
              />
            </div>
            <button
              onClick={handleCollect}
              disabled={!url || isCollecting}
              className="px-6 h-12 bg-gradient-to-r from-orange-400 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-orange-200 transition-all"
            >
              {isCollecting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              {isCollecting ? "采集中..." : "采集"}
            </button>
          </div>

          {/* 采集结果预览 */}
          {collectedProduct && (
            <div className="bg-white border rounded-xl overflow-hidden">
              {/* 头部：成功提示 + 基本信息 */}
              <div className="p-4 border-b bg-green-50">
                <div className="flex items-center gap-2 text-sm text-green-600 mb-3">
                  <CheckCircle className="h-4 w-4" />
                  采集成功
                </div>
                <h3 className="font-medium text-gray-800 leading-relaxed">{collectedProduct.title}</h3>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-xl font-bold text-orange-500">{collectedProduct.price}</span>
                  {collectedProduct.originalPrice && (
                    <span className="text-sm text-gray-400 line-through">{collectedProduct.originalPrice}</span>
                  )}
                </div>
              </div>

              {/* 主图/视频 */}
              <div className="p-4 border-b">
                <div className="text-sm text-gray-500 flex items-center gap-2 mb-3">
                  <Image className="h-4 w-4" />
                  主图/视频
                  <Badge className="bg-gray-100 text-gray-500 border-0 text-xs">
                    {collectedProduct.video ? "1视频 + " : ""}{collectedProduct.mainImages.length}图
                  </Badge>
                </div>
                <div className="flex gap-2">
                  {collectedProduct.video && (
                    <div className="relative w-16 h-16 bg-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Play className="h-6 w-6 text-white" />
                      <Badge className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs border-0 px-1">
                        视频
                      </Badge>
                    </div>
                  )}
                  {collectedProduct.mainImages.map((img, idx) => (
                    <div
                      key={idx}
                      className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 text-xs flex-shrink-0"
                    >
                      主图{idx + 1}
                    </div>
                  ))}
                </div>
              </div>

              {/* SKU信息 */}
              <div className="border-b">
                <button
                  onClick={() => toggleSection("skus")}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Tag className="h-4 w-4 text-orange-500" />
                    <span className="text-sm font-medium text-gray-800">SKU规格</span>
                    <Badge className="bg-orange-50 text-orange-600 border-0 text-xs">
                      {collectedProduct.skus.length} 个
                    </Badge>
                  </div>
                  {expandedSections.skus ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </button>
                {expandedSections.skus && (
                  <div className="px-4 pb-4">
                    <div className="space-y-2">
                      {collectedProduct.skus.map((sku) => (
                        <div
                          key={sku.id}
                          className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                        >
                          <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center text-gray-400 text-xs flex-shrink-0">
                            图
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-gray-800 truncate">
                              {sku.name}
                            </div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-orange-500 font-bold">¥{sku.price}</span>
                              {sku.originalPrice && (
                                <span className="text-xs text-gray-400 line-through">¥{sku.originalPrice}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 参数信息 */}
              <div className="border-b">
                <button
                  onClick={() => toggleSection("params")}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Info className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium text-gray-800">参数信息</span>
                    <Badge className="bg-blue-50 text-blue-600 border-0 text-xs">
                      {collectedProduct.params.length} 项
                    </Badge>
                  </div>
                  {expandedSections.params ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </button>
                {expandedSections.params && (
                  <div className="px-4 pb-4">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {collectedProduct.params.map((param, idx) => (
                        <div
                          key={idx}
                          className="flex bg-gray-50 rounded-lg px-3 py-2"
                        >
                          <span className="text-gray-500 flex-shrink-0 w-24">{param.name}</span>
                          <span className="text-gray-800 truncate" title={param.value}>
                            {param.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 商详图片 */}
              <div>
                <button
                  onClick={() => toggleSection("detailImages")}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium text-gray-800">商详图片</span>
                    <Badge className="bg-purple-50 text-purple-600 border-0 text-xs">
                      {collectedProduct.detailImages.length} 张
                    </Badge>
                  </div>
                  {expandedSections.detailImages ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </button>
                {expandedSections.detailImages && (
                  <div className="px-4 pb-4">
                    <div className="flex flex-wrap gap-2">
                      {collectedProduct.detailImages.map((img, idx) => (
                        <div
                          key={idx}
                          className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 text-xs"
                        >
                          {idx + 1}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        {/* ========== 区域2: 关联数据源 ========== */}
        {collectedProduct && (
          <section className="space-y-4 border-t pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-orange-500 text-white text-xs font-bold">
                  2
                </div>
                <h2 className="font-semibold text-gray-800">关联数据源</h2>
                <Badge className="bg-gray-100 text-gray-500 border-0 text-xs">可选</Badge>
              </div>
            </div>

            {configuredDataSources.length > 0 ? (
              <div className="space-y-3">
                <div className="flex gap-2 flex-wrap">
                  {configuredDataSources.map((ds) => (
                    <button
                      key={ds.id}
                      onClick={() => {
                        setSelectedDataSource(ds.id);
                        setMatchedFields(null);
                      }}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-all",
                        selectedDataSource === ds.id
                          ? "border-orange-300 bg-orange-50 text-orange-700"
                          : "border-gray-200 hover:border-gray-300 text-gray-600"
                      )}
                    >
                      <span className={selectedDataSource === ds.id ? "text-orange-500" : "text-gray-400"}>
                        {dataSourceIcons[ds.type]}
                      </span>
                      {ds.name}
                    </button>
                  ))}
                </div>

                {selectedDataSource && !matchedFields && (
                  <Button
                    onClick={handleMatchDataSource}
                    disabled={isMatching}
                    variant="outline"
                    className="rounded-lg"
                  >
                    {isMatching ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        匹配中...
                      </>
                    ) : (
                      <>
                        <Database className="h-4 w-4 mr-2" />
                        匹配数据
                      </>
                    )}
                  </Button>
                )}

                {matchedFields && (
                  <div className="bg-green-50 border border-green-200 rounded-xl p-4 space-y-2">
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      匹配成功，找到 {matchedFields.length} 个字段
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {matchedFields.map((field, idx) => (
                        <div key={idx} className="flex justify-between bg-white rounded-lg px-3 py-2">
                          <span className="text-gray-500">{field.name}</span>
                          <span className="text-gray-700 font-medium">{field.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="border rounded-xl p-4 text-center text-sm text-gray-500">
                <Database className="h-6 w-6 text-gray-300 mx-auto mb-2" />
                暂未配置数据源
                <button className="text-orange-500 hover:text-orange-600 font-medium ml-2">
                  去配置
                </button>
              </div>
            )}
          </section>
        )}

        {/* ========== 区域3: 关联模板 ========== */}
        {collectedProduct && (
          <section className="space-y-4 border-t pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-orange-500 text-white text-xs font-bold">
                  3
                </div>
                <h2 className="font-semibold text-gray-800">关联模板</h2>
                <Badge className="bg-gray-100 text-gray-500 border-0 text-xs">可选</Badge>
              </div>
            </div>

            {availableTemplates.length > 0 ? (
              <div className="space-y-3">
                <div className="flex gap-2 flex-wrap">
                  {availableTemplates.map((tpl) => (
                    <button
                      key={tpl.id}
                      onClick={() => handleSelectTemplate(tpl.id)}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-all",
                        selectedTemplate === tpl.id
                          ? "border-orange-300 bg-orange-50 text-orange-700"
                          : "border-gray-200 hover:border-gray-300 text-gray-600"
                      )}
                    >
                      <Truck className={cn(
                        "h-4 w-4",
                        selectedTemplate === tpl.id ? "text-orange-500" : "text-gray-400"
                      )} />
                      {tpl.name}
                    </button>
                  ))}
                </div>

                {templatePreview && (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-2">
                    <div className="flex items-center gap-2 text-sm text-blue-600">
                      <Truck className="h-4 w-4" />
                      模板配置预览
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {templatePreview.map((field, idx) => (
                        <div key={idx} className="flex justify-between bg-white rounded-lg px-3 py-2">
                          <span className="text-gray-500">{field.name}</span>
                          <span className="text-gray-700 font-medium">{field.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="border rounded-xl p-4 text-center text-sm text-gray-500">
                <FileText className="h-6 w-6 text-gray-300 mx-auto mb-2" />
                暂无可用模板
                <button className="text-orange-500 hover:text-orange-600 font-medium ml-2">
                  创建模板
                </button>
              </div>
            )}
          </section>
        )}

        {/* 底部提示 */}
        {collectedProduct && (
          <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-500">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 mt-0.5 text-gray-400" />
              <div>
                <strong className="text-gray-600">提示：</strong>
                数据源和模板为可选项。未关联时，将使用采集到的原始数据，后续步骤可手动编辑。
              </div>
            </div>
          </div>
        )}
      </div>
    </UploadLayout>
  );
}
