"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Package,
  Store,
  Database,
  FileText,
  CheckCircle,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/utils";

type Step = 1 | 2 | 3 | 4;

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [shopAuthorized, setShopAuthorized] = useState(false);

  const handleNext = () => {
    if (step < 4) {
      setStep((step + 1) as Step);
    } else {
      router.push("/");
    }
  };

  const handleSkip = () => {
    if (step < 4) {
      setStep((step + 1) as Step);
    } else {
      router.push("/");
    }
  };

  const handleAuthorize = () => {
    setTimeout(() => {
      setShopAuthorized(true);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-sm p-8">
        {/* Step 1: Welcome */}
        {step === 1 && (
          <div className="text-center space-y-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-500 rounded-2xl shadow-lg shadow-orange-200">
              <Package className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">欢迎使用</h1>
              <p className="text-lg text-gray-500 mt-1">
                淘宝商品一键上架工具
              </p>
            </div>

            <div className="border-t pt-6">
              <p className="text-sm text-gray-500 mb-6">
                只需 3 步，即可开始使用：
              </p>
              <div className="flex justify-center gap-6">
                {[
                  { num: 1, label: "授权店铺", required: true },
                  { num: 2, label: "配置数据源", required: false },
                  { num: 3, label: "创建模板", required: false },
                ].map((item, idx) => (
                  <div key={item.num} className="flex items-center">
                    <div className="flex flex-col items-center">
                      <div className={cn(
                        "w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm",
                        idx === 0
                          ? "bg-gradient-to-br from-orange-400 to-orange-500 text-white shadow-lg shadow-orange-200"
                          : "bg-gray-100 text-gray-500"
                      )}>
                        {item.num}
                      </div>
                      <span className="text-xs mt-2 text-gray-600">{item.label}</span>
                      <Badge className={cn(
                        "text-xs mt-1",
                        item.required
                          ? "bg-orange-50 text-orange-600 border-0"
                          : "bg-gray-50 text-gray-400 border-0"
                      )}>
                        {item.required ? "必须" : "推荐"}
                      </Badge>
                    </div>
                    {idx < 2 && (
                      <ArrowRight className="h-4 w-4 text-gray-300 mx-4" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            <Button onClick={handleNext} className="btn-primary-gradient rounded-xl w-full h-12">
              开始配置
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}

        {/* Step 2: Shop Authorization */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-800">店铺授权</h2>
                <p className="text-sm text-gray-400">步骤 1/3 · 必须</p>
              </div>
              <div className="p-2 bg-orange-50 rounded-xl">
                <Store className="h-5 w-5 text-orange-500" />
              </div>
            </div>

            <div className="border-t pt-6">
              {!shopAuthorized ? (
                <>
                  <p className="text-sm text-gray-500 mb-4">授权后可以：</p>
                  <ul className="text-sm space-y-2 mb-6">
                    {["获取店铺类目和品牌信息", "上传商品图片到图片空间", "发布商品到店铺"].map((item) => (
                      <li key={item} className="flex items-center gap-2 text-gray-600">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <Button onClick={handleAuthorize} className="btn-primary-gradient rounded-xl w-full h-12">
                    授权天猫/淘宝店铺
                    <ExternalLink className="h-4 w-4 ml-2" />
                  </Button>
                  <p className="text-xs text-gray-400 text-center mt-3">
                    点击后将跳转到淘宝登录页面
                  </p>
                </>
              ) : (
                <>
                  <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="font-medium text-green-700">授权成功！</span>
                    </div>
                    <div className="bg-white rounded-lg p-3 text-sm">
                      <div className="font-medium text-gray-800">九月的诗旗舰店</div>
                      <div className="text-gray-400 mt-1">店铺类型：天猫旗舰店</div>
                      <div className="text-gray-400">授权有效期：2026-02-01 至 2027-02-01</div>
                    </div>
                  </div>
                  <Button variant="outline" className="w-full rounded-xl mb-3">
                    + 添加更多店铺
                  </Button>
                  <Button onClick={handleNext} className="btn-primary-gradient rounded-xl w-full h-12">
                    下一步
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Datasource */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-800">数据源配置</h2>
                <p className="text-sm text-gray-400">步骤 2/3 · 推荐</p>
              </div>
              <div className="p-2 bg-orange-50 rounded-xl">
                <Database className="h-5 w-5 text-orange-500" />
              </div>
            </div>

            <div className="border-t pt-6">
              <p className="text-sm text-gray-500 mb-4">
                如果您在钉钉/飞书表格中维护了商品信息，可以关联后自动匹配填充。
              </p>

              <div className="grid grid-cols-3 gap-3 mb-6">
                {[
                  { icon: "📊", name: "钉钉表格", action: "配置" },
                  { icon: "📋", name: "飞书表格", action: "配置" },
                  { icon: "📁", name: "Excel", action: "上传" },
                ].map((item) => (
                  <button
                    key={item.name}
                    className="border rounded-xl p-4 text-center hover:border-orange-300 hover:bg-orange-50 transition-colors"
                  >
                    <div className="text-2xl mb-2">{item.icon}</div>
                    <div className="text-sm font-medium text-gray-700">{item.name}</div>
                    <div className="text-xs text-gray-400">{item.action}</div>
                  </button>
                ))}
              </div>

              <div className="bg-gray-50 rounded-xl p-3 text-sm text-gray-500 mb-6">
                💡 没有外部数据？可以跳过此步骤，后续手动填写字段
              </div>

              <div className="flex gap-3">
                <Button variant="outline" onClick={handleSkip} className="flex-1 rounded-xl">
                  跳过
                </Button>
                <Button onClick={handleNext} className="flex-1 btn-primary-gradient rounded-xl">
                  下一步
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Template */}
        {step === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-800">类目模板</h2>
                <p className="text-sm text-gray-400">步骤 3/3 · 推荐</p>
              </div>
              <div className="p-2 bg-orange-50 rounded-xl">
                <FileText className="h-5 w-5 text-orange-500" />
              </div>
            </div>

            <div className="border-t pt-6">
              <p className="text-sm text-gray-500 mb-4">
                从店铺已有商品中学习配置，后续上架同类目商品时自动套用。
              </p>

              <div className="border rounded-xl p-4 mb-4">
                <div className="text-sm font-medium text-gray-700 mb-3">
                  店铺商品（选择作为模板参考）
                </div>
                <div className="space-y-2">
                  {[
                    { name: "有机黑芝麻600g", category: "特色米/面粉/杂粮" },
                    { name: "有机核桃仁500g", category: "坚果/炒货" },
                    { name: "红薯粉条200g", category: "方便粉丝/米线" },
                  ].map((item) => (
                    <label
                      key={item.name}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input type="checkbox" className="h-4 w-4 rounded text-orange-500 focus:ring-orange-500" />
                      <div className="w-8 h-8 bg-gray-100 rounded-lg" />
                      <div className="flex-1">
                        <div className="text-sm text-gray-800">{item.name}</div>
                        <div className="text-xs text-gray-400">类目：{item.category}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 rounded-xl p-3 text-sm text-gray-500 mb-6">
                💡 可以跳过，后续在"模板管理"中创建
              </div>

              <div className="flex gap-3">
                <Button variant="outline" onClick={handleSkip} className="flex-1 rounded-xl">
                  跳过
                </Button>
                <Button onClick={handleNext} className="flex-1 btn-primary-gradient rounded-xl">
                  完成配置
                  <CheckCircle className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Progress dots */}
        <div className="flex justify-center gap-2 mt-8">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={cn(
                "w-2 h-2 rounded-full transition-colors",
                s === step ? "bg-orange-500" : "bg-gray-200"
              )}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
