"use client";

import { useState } from "react";
import { UploadLayout } from "@/components/upload";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  AlertCircle,
  Package,
  DollarSign,
  Barcode,
  Calculator,
  TrendingUp,
  TrendingDown,
  Percent,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface PriceStrategy {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  calculate: (originalPrice: number) => number;
}

interface SKU {
  id: number;
  name: string;
  image: string;
  merchantCode: string;
  organicCode: string;
  originalPrice: number; // 采集到的原价
  price: string;
  stock: string;
  enabled: boolean;
  barcode: string;
  netWeight: string;
  productInfoComplete: boolean;
}

// 内置价格策略
const priceStrategies: PriceStrategy[] = [
  {
    id: "fixed",
    name: "固定值",
    description: "手动输入价格",
    icon: <DollarSign className="h-4 w-4" />,
    calculate: (p) => p,
  },
  {
    id: "up_10",
    name: "上调 10%",
    description: "在原价基础上加价10%",
    icon: <TrendingUp className="h-4 w-4" />,
    calculate: (p) => Math.round(p * 1.1 * 100) / 100,
  },
  {
    id: "up_20",
    name: "上调 20%",
    description: "在原价基础上加价20%",
    icon: <TrendingUp className="h-4 w-4" />,
    calculate: (p) => Math.round(p * 1.2 * 100) / 100,
  },
  {
    id: "up_30",
    name: "上调 30%",
    description: "在原价基础上加价30%",
    icon: <TrendingUp className="h-4 w-4" />,
    calculate: (p) => Math.round(p * 1.3 * 100) / 100,
  },
  {
    id: "down_10",
    name: "下调 10%",
    description: "在原价基础上降价10%",
    icon: <TrendingDown className="h-4 w-4" />,
    calculate: (p) => Math.round(p * 0.9 * 100) / 100,
  },
  {
    id: "round_9",
    name: "整数抹零.9",
    description: "取整后减0.1（如40→39.9）",
    icon: <Calculator className="h-4 w-4" />,
    calculate: (p) => Math.ceil(p) - 0.1,
  },
  {
    id: "up_10_round_9",
    name: "上调10%后抹零.9",
    description: "先加价10%再取整减0.1",
    icon: <Calculator className="h-4 w-4" />,
    calculate: (p) => Math.ceil(p * 1.1) - 0.1,
  },
];

const initialSkus: SKU[] = [
  {
    id: 1,
    name: "有机黑芝麻600g(熟)",
    image: "",
    merchantCode: "SKU001",
    organicCode: "2490P18...",
    originalPrice: 39.9,
    price: "",
    stock: "",
    enabled: true,
    barcode: "6901234567",
    netWeight: "600g",
    productInfoComplete: true,
  },
  {
    id: 2,
    name: "有机黑芝麻730g(生)",
    image: "",
    merchantCode: "SKU002",
    organicCode: "2490P18...",
    originalPrice: 45.9,
    price: "",
    stock: "",
    enabled: true,
    barcode: "",
    netWeight: "730g",
    productInfoComplete: false,
  },
];

export default function UploadStep4() {
  const [skus, setSkus] = useState<SKU[]>(initialSkus);
  const [priceMode, setPriceMode] = useState<"fixed" | "strategy">("strategy");
  const [selectedStrategy, setSelectedStrategy] = useState<string>("up_10");
  const [showStrategyDropdown, setShowStrategyDropdown] = useState(false);

  const currentStrategy = priceStrategies.find((s) => s.id === selectedStrategy);

  const updateSku = (id: number, field: keyof SKU, value: string | boolean) => {
    setSkus((prev) =>
      prev.map((sku) => (sku.id === id ? { ...sku, [field]: value } : sku))
    );
  };

  // 应用价格策略到所有SKU
  const applyStrategy = (strategyId: string) => {
    const strategy = priceStrategies.find((s) => s.id === strategyId);
    if (!strategy || strategyId === "fixed") return;

    setSkus((prev) =>
      prev.map((sku) => ({
        ...sku,
        price: strategy.calculate(sku.originalPrice).toFixed(2),
      }))
    );
    setSelectedStrategy(strategyId);
    setShowStrategyDropdown(false);
  };

  // 切换到固定值模式
  const switchToFixed = () => {
    setPriceMode("fixed");
    setSelectedStrategy("fixed");
  };

  // 切换到策略模式
  const switchToStrategy = () => {
    setPriceMode("strategy");
    if (selectedStrategy === "fixed") {
      setSelectedStrategy("up_10");
    }
  };

  const hasEmptyPrices = skus.some((sku) => sku.enabled && !sku.price);

  return (
    <UploadLayout
      step={4}
      title="编辑SKU"
      prevHref="/upload/step3"
      nextHref="/upload/step5"
      nextDisabled={hasEmptyPrices}
    >
      <div className="space-y-6">
        {/* SKU List */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <Package className="h-4 w-4 text-orange-500" />
              </div>
              SKU列表（来源：采集 + 数据源）
            </h3>
            <Badge className="bg-orange-50 text-orange-600 border-0">
              {skus.length} 个规格
            </Badge>
          </div>
          <div className="border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-3 font-medium text-gray-600 w-12">#</th>
                  <th className="text-left p-3 font-medium text-gray-600">规格图</th>
                  <th className="text-left p-3 font-medium text-gray-600">规格名称</th>
                  <th className="text-left p-3 font-medium text-gray-600">商家编码</th>
                  <th className="text-left p-3 font-medium text-gray-600">有机编码</th>
                </tr>
              </thead>
              <tbody>
                {skus.map((sku, idx) => (
                  <tr key={sku.id} className="border-t hover:bg-gray-50 transition-colors">
                    <td className="p-3 text-gray-400">{idx + 1}</td>
                    <td className="p-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-xs text-gray-400">
                        图
                      </div>
                    </td>
                    <td className="p-3 font-medium text-gray-800">{sku.name}</td>
                    <td className="p-3 text-gray-500">{sku.merchantCode}</td>
                    <td className="p-3 text-gray-500">{sku.organicCode}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Price Strategy & Stock */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <DollarSign className="h-4 w-4 text-orange-500" />
              </div>
              价格库存
              <span className="text-red-500">*</span>
            </h3>
          </div>

          {/* Price Mode Toggle */}
          <div className="bg-gray-50 rounded-xl p-4 mb-4 space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">定价方式：</span>
              <div className="flex gap-2">
                <button
                  onClick={switchToFixed}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                    priceMode === "fixed"
                      ? "bg-orange-500 text-white shadow-lg shadow-orange-200"
                      : "bg-white border text-gray-600 hover:border-orange-300"
                  )}
                >
                  <DollarSign className="h-4 w-4 inline mr-1" />
                  固定值
                </button>
                <button
                  onClick={switchToStrategy}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                    priceMode === "strategy"
                      ? "bg-orange-500 text-white shadow-lg shadow-orange-200"
                      : "bg-white border text-gray-600 hover:border-orange-300"
                  )}
                >
                  <Calculator className="h-4 w-4 inline mr-1" />
                  价格策略
                </button>
              </div>
            </div>

            {/* Strategy Selector */}
            {priceMode === "strategy" && (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">选择策略：</span>
                <div className="relative">
                  <button
                    onClick={() => setShowStrategyDropdown(!showStrategyDropdown)}
                    className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg text-sm hover:border-orange-300 transition-colors min-w-[200px] justify-between"
                  >
                    <span className="flex items-center gap-2">
                      {currentStrategy?.icon}
                      <span className="font-medium">{currentStrategy?.name}</span>
                    </span>
                    <ChevronDown className={cn(
                      "h-4 w-4 text-gray-400 transition-transform",
                      showStrategyDropdown && "rotate-180"
                    )} />
                  </button>

                  {showStrategyDropdown && (
                    <div className="absolute top-full left-0 mt-1 w-72 bg-white border rounded-xl shadow-lg z-10 py-2">
                      {priceStrategies.filter((s) => s.id !== "fixed").map((strategy) => (
                        <button
                          key={strategy.id}
                          onClick={() => applyStrategy(strategy.id)}
                          className={cn(
                            "w-full px-4 py-2.5 text-left hover:bg-orange-50 transition-colors flex items-start gap-3",
                            selectedStrategy === strategy.id && "bg-orange-50"
                          )}
                        >
                          <span className={cn(
                            "mt-0.5",
                            selectedStrategy === strategy.id ? "text-orange-500" : "text-gray-400"
                          )}>
                            {strategy.icon}
                          </span>
                          <div>
                            <div className={cn(
                              "font-medium text-sm",
                              selectedStrategy === strategy.id ? "text-orange-600" : "text-gray-800"
                            )}>
                              {strategy.name}
                            </div>
                            <div className="text-xs text-gray-500">{strategy.description}</div>
                          </div>
                          {selectedStrategy === strategy.id && (
                            <CheckCircle className="h-4 w-4 text-orange-500 ml-auto mt-0.5" />
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <Button
                  onClick={() => applyStrategy(selectedStrategy)}
                  variant="outline"
                  size="sm"
                  className="rounded-lg"
                >
                  应用策略
                </Button>
              </div>
            )}

            {priceMode === "strategy" && selectedStrategy !== "fixed" && (
              <div className="text-xs text-gray-500 flex items-center gap-1">
                <Percent className="h-3 w-3" />
                策略将基于采集到的原价计算，你也可以在下方手动调整单个SKU的价格
              </div>
            )}
          </div>

          {/* Price & Stock Table */}
          <div className="border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-3 font-medium text-gray-600 w-12">#</th>
                  <th className="text-left p-3 font-medium text-gray-600">规格名称</th>
                  <th className="text-left p-3 font-medium text-gray-600 w-24">原价</th>
                  <th className="text-left p-3 font-medium text-gray-600 w-32">
                    售价(元)<span className="text-red-500">*</span>
                  </th>
                  <th className="text-left p-3 font-medium text-gray-600 w-24">库存</th>
                  <th className="text-left p-3 font-medium text-gray-600 w-20">上架</th>
                </tr>
              </thead>
              <tbody>
                {skus.map((sku, idx) => {
                  const priceDiff = sku.price
                    ? ((parseFloat(sku.price) - sku.originalPrice) / sku.originalPrice) * 100
                    : null;

                  return (
                    <tr key={sku.id} className="border-t hover:bg-gray-50 transition-colors">
                      <td className="p-3 text-gray-400">{idx + 1}</td>
                      <td className="p-3 text-gray-800">{sku.name}</td>
                      <td className="p-3 text-gray-400">
                        ¥{sku.originalPrice.toFixed(2)}
                      </td>
                      <td className="p-3">
                        <div className="relative">
                          <Input
                            type="number"
                            placeholder="0.00"
                            value={sku.price}
                            onChange={(e) => updateSku(sku.id, "price", e.target.value)}
                            className="w-full rounded-lg border-gray-200 focus:border-orange-300 focus:ring-orange-200 pr-14"
                          />
                          {priceDiff !== null && (
                            <span
                              className={cn(
                                "absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium",
                                priceDiff > 0 ? "text-green-600" : priceDiff < 0 ? "text-red-600" : "text-gray-400"
                              )}
                            >
                              {priceDiff > 0 ? "+" : ""}{priceDiff.toFixed(0)}%
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="p-3">
                        <Input
                          type="number"
                          placeholder="0"
                          value={sku.stock}
                          onChange={(e) => updateSku(sku.id, "stock", e.target.value)}
                          className="w-full rounded-lg border-gray-200 focus:border-orange-300 focus:ring-orange-200"
                        />
                      </td>
                      <td className="p-3">
                        <input
                          type="checkbox"
                          checked={sku.enabled}
                          onChange={(e) => updateSku(sku.id, "enabled", e.target.checked)}
                          className="h-4 w-4 rounded text-orange-500 focus:ring-orange-500"
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Product Info */}
        <div>
          <h3 className="text-sm font-medium text-gray-800 flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-orange-50 rounded-lg">
              <Barcode className="h-4 w-4 text-orange-500" />
            </div>
            SKU产品信息（来源：采集 + 数据源）
          </h3>
          <div className="border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-3 font-medium text-gray-600 w-12">#</th>
                  <th className="text-left p-3 font-medium text-gray-600">规格名称</th>
                  <th className="text-left p-3 font-medium text-gray-600">条形码</th>
                  <th className="text-left p-3 font-medium text-gray-600">净含量</th>
                  <th className="text-left p-3 font-medium text-gray-600 w-20">状态</th>
                </tr>
              </thead>
              <tbody>
                {skus.map((sku, idx) => (
                  <tr key={sku.id} className="border-t hover:bg-gray-50 transition-colors">
                    <td className="p-3 text-gray-400">{idx + 1}</td>
                    <td className="p-3 text-gray-800">{sku.name}</td>
                    <td className="p-3 text-gray-500">
                      {sku.barcode || (
                        <span className="text-gray-300">未填写</span>
                      )}
                    </td>
                    <td className="p-3 text-gray-500">{sku.netWeight}</td>
                    <td className="p-3">
                      {sku.productInfoComplete ? (
                        <Badge className="bg-green-50 text-green-600 border-green-200">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          完整
                        </Badge>
                      ) : (
                        <Badge className="bg-red-50 text-red-600 border-red-200">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          缺失
                        </Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </UploadLayout>
  );
}
