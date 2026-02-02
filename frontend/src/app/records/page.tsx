"use client";

import { MainLayout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Search,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  Clock,
  History,
  Image,
  MoreHorizontal,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Record {
  id: number;
  title: string;
  sourceUrl: string;
  targetItemId: string | null;
  status: "success" | "failed" | "pending";
  createdAt: string;
  category: string;
}

const records: Record[] = [
  {
    id: 1,
    title: "有机白沙花生780g 五谷杂粮",
    sourceUrl: "https://item.taobao.com/item.htm?id=123",
    targetItemId: "789456123",
    status: "success",
    createdAt: "2026-02-01 14:30",
    category: "粮油调味/米/面粉/杂粮",
  },
  {
    id: 2,
    title: "有机鹰嘴豆950g 即食五谷",
    sourceUrl: "https://item.taobao.com/item.htm?id=124",
    targetItemId: "789456124",
    status: "success",
    createdAt: "2026-02-01 13:20",
    category: "粮油调味/米/面粉/杂粮",
  },
  {
    id: 3,
    title: "有机红芸豆500g",
    sourceUrl: "https://item.taobao.com/item.htm?id=125",
    targetItemId: null,
    status: "pending",
    createdAt: "2026-02-01 12:10",
    category: "粮油调味/米/面粉/杂粮",
  },
  {
    id: 4,
    title: "有机黑米1kg",
    sourceUrl: "https://item.taobao.com/item.htm?id=126",
    targetItemId: null,
    status: "failed",
    createdAt: "2026-02-01 11:00",
    category: "粮油调味/米/面粉/杂粮",
  },
];

const statusConfig = {
  success: {
    label: "成功",
    color: "bg-green-50 text-green-600 border-green-200",
    icon: CheckCircle,
  },
  failed: {
    label: "失败",
    color: "bg-red-50 text-red-600 border-red-200",
    icon: AlertCircle,
  },
  pending: {
    label: "待处理",
    color: "bg-yellow-50 text-yellow-600 border-yellow-200",
    icon: Clock,
  },
};

export default function RecordsPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">上架记录</h1>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input placeholder="搜索商品..." className="pl-10 w-64 rounded-xl border-gray-200" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <History className="h-4 w-4 text-orange-500" />
              </div>
              全部记录
            </h3>
            <div className="flex gap-2">
              {["全部", "成功", "失败", "待处理"].map((tab, idx) => (
                <button
                  key={tab}
                  className={cn(
                    "px-4 py-1.5 rounded-lg text-sm transition-colors",
                    idx === 0
                      ? "bg-orange-50 text-orange-600 font-medium"
                      : "text-gray-400 hover:bg-gray-50"
                  )}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <div className="border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-4 font-medium text-gray-600">商品</th>
                  <th className="text-left p-4 font-medium text-gray-600">类目</th>
                  <th className="text-left p-4 font-medium text-gray-600">时间</th>
                  <th className="text-left p-4 font-medium text-gray-600">状态</th>
                  <th className="text-left p-4 font-medium text-gray-600">操作</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => {
                  const StatusIcon = statusConfig[record.status].icon;
                  return (
                    <tr key={record.id} className="border-t hover:bg-gray-50 transition-colors">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                            <Image className="h-5 w-5 text-gray-300" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-800">{record.title}</div>
                            {record.targetItemId && (
                              <div className="text-xs text-gray-400">
                                ID: {record.targetItemId}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-gray-500">
                        {record.category}
                      </td>
                      <td className="p-4 text-gray-400">
                        {record.createdAt}
                      </td>
                      <td className="p-4">
                        <Badge className={cn("border", statusConfig[record.status].color)}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {statusConfig[record.status].label}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex gap-1">
                          {record.targetItemId && (
                            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-orange-500">
                              <ExternalLink className="h-4 w-4" />
                            </Button>
                          )}
                          {record.status === "pending" && (
                            <Button variant="ghost" size="sm" className="text-orange-500 hover:text-orange-600">
                              继续
                            </Button>
                          )}
                          {record.status === "failed" && (
                            <Button variant="ghost" size="sm" className="text-orange-500 hover:text-orange-600">
                              重试
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
