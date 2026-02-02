"use client";

import { useState } from "react";
import { UploadLayout } from "@/components/upload";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, ChevronRight, FolderTree } from "lucide-react";
import { cn } from "@/lib/utils";

const categoryTree = {
  level1: [
    { id: 1, name: "粮油调味/速食" },
    { id: 2, name: "咖啡/麦片" },
    { id: 3, name: "零食/坚果" },
  ],
  level2: [
    { id: 11, name: "米/面粉/杂粮" },
    { id: 12, name: "低温乳类" },
    { id: 13, name: "调味品" },
  ],
  level3: [
    { id: 111, name: "特色米/面粉" },
    { id: 112, name: "豆类" },
    { id: 113, name: "米类" },
    { id: 114, name: "杂粮组合" },
  ],
};

export default function UploadStep2() {
  const [selected, setSelected] = useState({
    level1: 1,
    level2: 11,
    level3: 111,
  });

  return (
    <UploadLayout
      step={2}
      title="选择目标类目"
      prevHref="/upload"
      nextHref="/upload/step3"
    >
      <div className="space-y-6">
        {/* Source Category */}
        <div className="bg-gray-50 rounded-xl p-4">
          <div className="text-sm text-gray-400 mb-1">源商品类目</div>
          <div className="font-medium text-gray-800">食品 &gt; 坚果 &gt; 花生</div>
        </div>

        {/* Target Category Selector */}
        <div>
          <label className="text-sm font-medium text-gray-700 mb-3 block">目标类目</label>
          <div className="grid grid-cols-3 gap-3">
            {/* Level 1 */}
            <div className="border rounded-xl overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 text-xs font-medium text-gray-500">
                一级类目
              </div>
              <div className="max-h-48 overflow-y-auto">
                {categoryTree.level1.map((cat) => (
                  <div
                    key={cat.id}
                    onClick={() => setSelected({ ...selected, level1: cat.id })}
                    className={cn(
                      "px-4 py-3 text-sm cursor-pointer flex items-center justify-between transition-colors",
                      selected.level1 === cat.id
                        ? "bg-orange-50 text-orange-600 font-medium"
                        : "hover:bg-gray-50 text-gray-700"
                    )}
                  >
                    {cat.name}
                    {selected.level1 === cat.id && (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Level 2 */}
            <div className="border rounded-xl overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 text-xs font-medium text-gray-500">
                二级类目
              </div>
              <div className="max-h-48 overflow-y-auto">
                {categoryTree.level2.map((cat) => (
                  <div
                    key={cat.id}
                    onClick={() => setSelected({ ...selected, level2: cat.id })}
                    className={cn(
                      "px-4 py-3 text-sm cursor-pointer flex items-center justify-between transition-colors",
                      selected.level2 === cat.id
                        ? "bg-orange-50 text-orange-600 font-medium"
                        : "hover:bg-gray-50 text-gray-700"
                    )}
                  >
                    {cat.name}
                    {selected.level2 === cat.id && (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Level 3 */}
            <div className="border rounded-xl overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 text-xs font-medium text-gray-500">
                三级类目
              </div>
              <div className="max-h-48 overflow-y-auto">
                {categoryTree.level3.map((cat) => (
                  <div
                    key={cat.id}
                    onClick={() => setSelected({ ...selected, level3: cat.id })}
                    className={cn(
                      "px-4 py-3 text-sm cursor-pointer flex items-center justify-between transition-colors",
                      selected.level3 === cat.id
                        ? "bg-orange-50 text-orange-600 font-medium"
                        : "hover:bg-gray-50 text-gray-700"
                    )}
                  >
                    {cat.name}
                    {selected.level3 === cat.id && (
                      <CheckCircle className="h-4 w-4" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Template Info */}
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
            <div>
              <div className="font-medium text-sm text-green-800">
                特色米/面粉 模板
                <Badge className="ml-2 bg-green-100 text-green-700 border-0">
                  来源：有机黑芝麻600g
                </Badge>
              </div>
              <div className="text-sm text-green-600 mt-1">
                包含：发货地、物流模板、售后承诺、厂家信息
              </div>
            </div>
          </div>
        </div>
      </div>
    </UploadLayout>
  );
}
