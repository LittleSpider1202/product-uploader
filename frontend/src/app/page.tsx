"use client";

import Link from "next/link";
import { MainLayout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Upload,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Database,
  FileText,
  Image,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Mock data
const stats = {
  todayCount: 3,
  monthCount: 28,
  successRate: 96,
};

const configStatus = {
  shop: { ok: true, label: "店铺授权有效", detail: "有效期至 2027-02-01" },
  datasource: { ok: true, label: "数据源已配置", detail: "钉钉表格 89条记录" },
  template: { ok: true, label: "类目模板", detail: "3 个模板" },
};

const recentRecords = [
  {
    id: 1,
    title: "有机白沙花生780g",
    time: "10分钟前",
    status: "success",
  },
  {
    id: 2,
    title: "有机鹰嘴豆950g",
    time: "1小时前",
    status: "success",
  },
  {
    id: 3,
    title: "有机红芸豆500g",
    time: "2小时前",
    status: "pending",
  },
];

export default function HomePage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Quick Actions & Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Upload Card */}
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6 border border-orange-200">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="p-4 bg-gradient-to-br from-orange-400 to-orange-500 rounded-2xl shadow-lg shadow-orange-200">
                <Upload className="h-8 w-8 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">上架商品</h2>
                <p className="text-sm text-gray-500 mt-1">
                  输入链接，开始上架
                </p>
              </div>
              <Link href="/upload">
                <Button className="btn-primary-gradient rounded-xl px-8">
                  开始上架
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats Card */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2 mb-4">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <TrendingUp className="h-4 w-4 text-orange-500" />
              </div>
              数据概览
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <div className="text-3xl font-bold text-gray-800">{stats.todayCount}</div>
                <div className="text-xs text-gray-400 mt-1">今日上架</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <div className="text-3xl font-bold text-gray-800">{stats.monthCount}</div>
                <div className="text-xs text-gray-400 mt-1">本月上架</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-xl">
                <div className="text-3xl font-bold text-green-600">
                  {stats.successRate}%
                </div>
                <div className="text-xs text-gray-400 mt-1">成功率</div>
              </div>
            </div>
          </div>
        </div>

        {/* Config Status */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 flex items-center gap-2 mb-4">
            <div className="p-1.5 bg-orange-50 rounded-lg">
              <CheckCircle className="h-4 w-4 text-orange-500" />
            </div>
            配置状态
          </h3>
          <div className="space-y-3">
            {Object.entries(configStatus).map(([key, item]) => (
              <div
                key={key}
                className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  {item.ok ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-500" />
                  )}
                  <span className="text-sm font-medium text-gray-700">{item.label}</span>
                </div>
                <span className="text-sm text-gray-400">
                  {item.detail}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Records */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <div className="p-1.5 bg-orange-50 rounded-lg">
                <Clock className="h-4 w-4 text-orange-500" />
              </div>
              最近上架
            </h3>
            <Link href="/records">
              <Button variant="ghost" size="sm" className="text-orange-500 hover:text-orange-600 hover:bg-orange-50">
                查看全部
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </div>
          <div className="space-y-3">
            {recentRecords.map((record) => (
              <div
                key={record.id}
                className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center">
                    <Image className="h-5 w-5 text-gray-400" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">{record.title}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-gray-400">
                    {record.time}
                  </span>
                  {record.status === "success" ? (
                    <Badge className="bg-green-50 text-green-600 border border-green-200">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      成功
                    </Badge>
                  ) : (
                    <Badge className="bg-yellow-50 text-yellow-600 border border-yellow-200">
                      <Clock className="h-3 w-3 mr-1" />
                      待处理
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
