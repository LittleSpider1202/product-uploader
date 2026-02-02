"use client";

import { useState } from "react";
import { UploadLayout } from "@/components/upload";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  AlertCircle,
  Image,
  Package,
  DollarSign,
  Clock,
  Warehouse,
  Rocket,
  ClipboardCheck,
  Eye,
} from "lucide-react";
import { cn } from "@/lib/utils";

type UploadMode = "now" | "scheduled" | "warehouse";

interface CheckItem {
  label: string;
  detail: string;
  ok: boolean;
}

const checkItems: CheckItem[] = [
  {
    label: "必填字段已完成",
    detail: "(22/22)",
    ok: true,
  },
  {
    label: "图片已上传",
    detail: "(8张)",
    ok: true,
  },
  {
    label: "SKU信息完整",
    detail: "(2个)",
    ok: true,
  },
  {
    label: "价格库存已填写",
    detail: "",
    ok: true,
  },
  {
    label: "白底图未生成",
    detail: "（可选）",
    ok: false,
  },
];

export default function UploadStep5() {
  const [uploadMode, setUploadMode] = useState<UploadMode>("warehouse");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleSubmit = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitSuccess(true);
    }, 2000);
  };

  if (submitSuccess) {
    return (
      <UploadLayout
        step={5}
        title="上架成功"
        nextLabel="继续上架"
        nextHref="/upload"
      >
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-400 to-green-500 rounded-2xl shadow-lg shadow-green-200 mb-4">
            <CheckCircle className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">商品上架成功！</h2>
          <p className="text-gray-500 mb-6">
            商品已{uploadMode === "warehouse" ? "放入仓库" : "成功上架"}
          </p>
          <div className="bg-gray-50 rounded-xl p-4 max-w-md mx-auto">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gray-200 rounded-xl flex items-center justify-center text-gray-400">
                图
              </div>
              <div className="text-left">
                <div className="font-medium text-gray-800">有机黑芝麻600g 九月的诗</div>
                <div className="text-sm text-gray-400">
                  商品ID: 123456789
                </div>
                <Badge className={cn(
                  "mt-2",
                  uploadMode === "warehouse"
                    ? "bg-blue-50 text-blue-600 border-blue-200"
                    : "bg-green-50 text-green-600 border-green-200"
                )}>
                  {uploadMode === "warehouse" ? "仓库中" : "已上架"}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </UploadLayout>
    );
  }

  return (
    <UploadLayout
      step={5}
      title="提交上架"
      prevHref="/upload/step4"
      nextLabel={isSubmitting ? "提交中..." : "提交上架"}
      onNext={handleSubmit}
      nextDisabled={isSubmitting}
    >
      <div className="space-y-6">
        {/* Pre-submit Check */}
        <div>
          <h3 className="text-sm font-medium text-gray-800 flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-orange-50 rounded-lg">
              <ClipboardCheck className="h-4 w-4 text-orange-500" />
            </div>
            上架前检查
          </h3>
          <div className="border rounded-xl p-4 space-y-3">
            {checkItems.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3"
              >
                <div
                  className={cn(
                    "p-1 rounded-full",
                    item.ok ? "bg-green-50" : "bg-yellow-50"
                  )}
                >
                  {item.ok ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-yellow-500" />
                  )}
                </div>
                <span className={cn(
                  "text-sm",
                  item.ok ? "text-gray-700" : "text-yellow-600"
                )}>
                  {item.label}
                </span>
                {item.detail && (
                  <span className="text-sm text-gray-400">{item.detail}</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Product Preview */}
        <div>
          <h3 className="text-sm font-medium text-gray-800 flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-orange-50 rounded-lg">
              <Eye className="h-4 w-4 text-orange-500" />
            </div>
            商品预览
          </h3>
          <div className="border rounded-xl p-4">
            <div className="flex gap-4">
              <div className="w-24 h-24 bg-gray-100 rounded-xl flex items-center justify-center text-gray-400">
                主图
              </div>
              <div className="flex-1">
                <div className="font-medium text-gray-800">
                  有机黑芝麻600g 九月的诗 五谷杂粮
                </div>
                <div className="text-lg font-bold text-orange-500 mt-1">
                  ¥XX.XX
                </div>
                <div className="text-sm text-gray-400 mt-2 space-y-1">
                  <div className="flex items-center gap-2">
                    <Package className="h-3.5 w-3.5" />
                    SKU: 2个
                  </div>
                  <div>类目: 粮油调味 &gt; 米/面粉/杂粮 &gt; 特色米</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Mode */}
        <div>
          <h3 className="text-sm font-medium text-gray-800 flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-orange-50 rounded-lg">
              <Rocket className="h-4 w-4 text-orange-500" />
            </div>
            上架方式
          </h3>
          <div className="space-y-2">
            <label
              className={cn(
                "flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-colors",
                uploadMode === "now"
                  ? "border-orange-300 bg-orange-50"
                  : "hover:bg-gray-50"
              )}
            >
              <input
                type="radio"
                name="uploadMode"
                checked={uploadMode === "now"}
                onChange={() => setUploadMode("now")}
                className="h-4 w-4 text-orange-500 focus:ring-orange-500"
              />
              <Rocket className={cn(
                "h-4 w-4",
                uploadMode === "now" ? "text-orange-500" : "text-gray-400"
              )} />
              <span className={cn(
                "text-sm",
                uploadMode === "now" ? "text-orange-600 font-medium" : "text-gray-700"
              )}>立刻上架</span>
            </label>

            <label
              className={cn(
                "flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-colors",
                uploadMode === "scheduled"
                  ? "border-orange-300 bg-orange-50"
                  : "hover:bg-gray-50"
              )}
            >
              <input
                type="radio"
                name="uploadMode"
                checked={uploadMode === "scheduled"}
                onChange={() => setUploadMode("scheduled")}
                className="h-4 w-4 text-orange-500 focus:ring-orange-500"
              />
              <Clock className={cn(
                "h-4 w-4",
                uploadMode === "scheduled" ? "text-orange-500" : "text-gray-400"
              )} />
              <span className={cn(
                "text-sm",
                uploadMode === "scheduled" ? "text-orange-600 font-medium" : "text-gray-700"
              )}>定时上架</span>
              {uploadMode === "scheduled" && (
                <input
                  type="datetime-local"
                  className="ml-auto text-sm border border-orange-200 rounded-lg px-3 py-1.5 focus:border-orange-300 focus:ring-orange-200"
                />
              )}
            </label>

            <label
              className={cn(
                "flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-colors",
                uploadMode === "warehouse"
                  ? "border-orange-300 bg-orange-50"
                  : "hover:bg-gray-50"
              )}
            >
              <input
                type="radio"
                name="uploadMode"
                checked={uploadMode === "warehouse"}
                onChange={() => setUploadMode("warehouse")}
                className="h-4 w-4 text-orange-500 focus:ring-orange-500"
              />
              <Warehouse className={cn(
                "h-4 w-4",
                uploadMode === "warehouse" ? "text-orange-500" : "text-gray-400"
              )} />
              <span className={cn(
                "text-sm",
                uploadMode === "warehouse" ? "text-orange-600 font-medium" : "text-gray-700"
              )}>放入仓库</span>
            </label>
          </div>
        </div>
      </div>
    </UploadLayout>
  );
}
