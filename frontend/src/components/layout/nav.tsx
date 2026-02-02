"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Home,
  Upload,
  History,
  FileText,
  Settings,
  Package,
} from "lucide-react";

const navItems = [
  { href: "/", label: "首页", icon: Home },
  { href: "/upload", label: "上架", icon: Upload },
  { href: "/records", label: "记录", icon: History },
  { href: "/settings", label: "设置", icon: Settings },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg shadow-orange-200">
              <Package className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-gray-800">淘宝商品一键上架</span>
            </div>
          </Link>

          {/* Navigation */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href ||
                (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-sm rounded-xl transition-colors",
                    isActive
                      ? "bg-orange-50 text-orange-600 font-medium"
                      : "text-gray-500 hover:bg-gray-50 hover:text-gray-700"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>

          {/* Shop Info */}
          <div className="flex items-center gap-2 text-sm">
            <span className="h-2 w-2 rounded-full bg-green-500"></span>
            <span className="text-gray-600">九月的诗旗舰店</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
