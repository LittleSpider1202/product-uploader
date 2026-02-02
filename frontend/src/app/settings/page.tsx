"use client";

import { MainLayout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Store,
  Database,
  RefreshCw,
  Trash2,
  Plus,
  CheckCircle,
  ExternalLink,
  FileText,
  Edit,
  FolderTree,
} from "lucide-react";

interface Shop {
  id: number;
  name: string;
  type: string;
  expiresAt: string;
  status: "active" | "expired";
}

interface Datasource {
  id: number;
  type: string;
  name: string;
  records: number;
  lastSynced: string;
}

interface Template {
  id: number;
  category: string;
  sourceProduct: string;
  fields: string[];
  createdAt: string;
}

const shops: Shop[] = [
  {
    id: 1,
    name: "九月的诗旗舰店",
    type: "天猫旗舰店",
    expiresAt: "2027-02-01",
    status: "active",
  },
];

const datasources: Datasource[] = [
  {
    id: 1,
    type: "dingtalk",
    name: "有机证书管理表",
    records: 89,
    lastSynced: "10分钟前",
  },
];

const templates: Template[] = [
  {
    id: 1,
    category: "粮油调味/米/面粉/杂粮/特色米",
    sourceProduct: "有机黑芝麻600g",
    fields: ["发货地", "物流模板", "售后承诺", "厂家信息", "生产许可证"],
    createdAt: "2026-01-30",
  },
  {
    id: 2,
    category: "零食/坚果/特产/坚果炒货",
    sourceProduct: "有机核桃仁500g",
    fields: ["发货地", "物流模板", "售后承诺", "厂家信息"],
    createdAt: "2026-01-28",
  },
  {
    id: 3,
    category: "粮油调味/方便速食/方便粉丝",
    sourceProduct: "红薯粉条200g",
    fields: ["发货地", "物流模板", "售后承诺"],
    createdAt: "2026-01-25",
  },
];

export default function SettingsPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <h1 className="text-xl font-bold text-gray-800">设置</h1>

        {/* Shop Authorization */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <Store className="h-4 w-4 text-orange-500" />
              </div>
              店铺授权
            </h3>
            <Button className="btn-primary-gradient rounded-xl">
              <Plus className="h-4 w-4 mr-2" />
              添加店铺
            </Button>
          </div>
          <div className="space-y-3">
            {shops.map((shop) => (
              <div
                key={shop.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center">
                    <Store className="h-6 w-6 text-orange-500" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-800">{shop.name}</div>
                    <div className="text-sm text-gray-400">
                      {shop.type}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      {shop.status === "active" ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm text-green-600 font-medium">授权有效</span>
                        </>
                      ) : (
                        <Badge variant="destructive">已过期</Badge>
                      )}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      到期时间：{shop.expiresAt}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="rounded-lg">
                      <RefreshCw className="h-4 w-4 mr-1" />
                      刷新
                    </Button>
                    <Button variant="outline" size="sm" className="rounded-lg text-gray-400 hover:text-red-500">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Datasource Configuration */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <Database className="h-4 w-4 text-orange-500" />
              </div>
              数据源配置
            </h3>
            <Button className="btn-primary-gradient rounded-xl">
              <Plus className="h-4 w-4 mr-2" />
              添加数据源
            </Button>
          </div>
          <div className="space-y-3">
            {datasources.length > 0 ? (
              datasources.map((ds) => (
                <div
                  key={ds.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl">
                      📊
                    </div>
                    <div>
                      <div className="font-medium text-gray-800">{ds.name}</div>
                      <div className="text-sm text-gray-400">
                        钉钉多维表格 · {ds.records} 条记录
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-600">最后同步</div>
                      <div className="text-xs text-gray-400">
                        {ds.lastSynced}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="rounded-lg">
                        <RefreshCw className="h-4 w-4 mr-1" />
                        同步
                      </Button>
                      <Button variant="outline" size="sm" className="rounded-lg">
                        <ExternalLink className="h-4 w-4 mr-1" />
                        配置
                      </Button>
                      <Button variant="outline" size="sm" className="rounded-lg text-gray-400 hover:text-red-500">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Database className="h-12 w-12 mx-auto mb-4 opacity-30" />
                <p className="font-medium text-gray-500">暂无数据源</p>
                <p className="text-sm mt-1">
                  添加钉钉/飞书表格，自动匹配商品信息
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Category Templates */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <FileText className="h-4 w-4 text-orange-500" />
              </div>
              类目模板
            </h3>
            <Button className="btn-primary-gradient rounded-xl">
              <Plus className="h-4 w-4 mr-2" />
              创建模板
            </Button>
          </div>

          {templates.length > 0 ? (
            <div className="space-y-3">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className="flex items-start justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="flex gap-4">
                    <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center flex-shrink-0">
                      <FolderTree className="h-6 w-6 text-orange-500" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-800 text-sm">
                        {template.category}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        来源商品：{template.sourceProduct}
                      </div>
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {template.fields.map((field) => (
                          <Badge
                            key={field}
                            className="bg-orange-50 text-orange-600 border-0 text-xs font-normal"
                          >
                            {field}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-xs text-gray-400">
                      创建于 {template.createdAt}
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" className="text-gray-400 hover:text-orange-500">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-gray-400 hover:text-red-500">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-30" />
              <p className="font-medium text-gray-500">暂无模板</p>
              <p className="text-sm mt-1">
                从店铺已有商品创建模板，后续上架时自动应用
              </p>
              <Button className="btn-primary-gradient rounded-xl mt-6">
                <Plus className="h-4 w-4 mr-2" />
                创建第一个模板
              </Button>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
