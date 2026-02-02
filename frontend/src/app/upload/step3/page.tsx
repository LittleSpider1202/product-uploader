"use client";

import { useState } from "react";
import { UploadLayout } from "@/components/upload";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Image,
  FileText,
  Factory,
  Truck,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Sparkles,
  AlertCircle,
  FolderOpen,
  Folder,
  Upload,
  CheckCircle,
  Loader2,
  RefreshCw,
  Plus,
} from "lucide-react";
import { cn } from "@/lib/utils";

type FieldStatus = "completed" | "pending" | "generate" | "optional" | "uploading";
type FieldType = "text" | "image" | "video";

interface Field {
  name: string;
  value: string;
  source: string;
  status: FieldStatus;
  required: boolean;
  type: FieldType;
  imageCount?: number;
  uploadedCount?: number;
}

interface FieldGroup {
  title: string;
  icon: React.ReactNode;
  fields: Field[];
}

interface FolderNode {
  id: string;
  name: string;
  children?: FolderNode[];
}

// 模拟千牛素材库目录结构（树形）
const materialFolderTree: FolderNode[] = [
  { id: "all", name: "全部素材" },
  { id: "ai", name: "[官方] 智能创作" },
  {
    id: "product",
    name: "产品",
    children: [
      {
        id: "organic-drink",
        name: "有机冲饮类",
        children: [
          { id: "od-1", name: "黑芝麻糊" },
          { id: "od-2", name: "核桃粉" },
        ],
      },
      {
        id: "organic-dry",
        name: "有机干货类",
        children: [
          { id: "dry-1", name: "枸杞" },
          { id: "dry-2", name: "红枣" },
        ],
      },
      {
        id: "organic-grain",
        name: "有机杂粮类",
        children: [
          { id: "grain-1", name: "玉米大碴子（糯）" },
          { id: "grain-2", name: "玉米碴子" },
          { id: "grain-3", name: "花生（红）" },
          { id: "grain-4", name: "黑芝麻(熟)600g" },
          { id: "grain-5", name: "黑芝麻(生)730g" },
        ],
      },
    ],
  },
  {
    id: "other",
    name: "其他",
    children: [
      { id: "other-1", name: "有机组合类" },
      { id: "other-2", name: "智能背景图" },
      { id: "other-3", name: "有机海产品" },
    ],
  },
];

// 模拟淘宝schema返回的字段规则
const initialFieldGroups: FieldGroup[] = [
  {
    title: "图文描述",
    icon: <Image className="h-4 w-4" />,
    fields: [
      { name: "1:1主图(5张)", value: "5张待上传", source: "采集", status: "pending", required: true, type: "image", imageCount: 5, uploadedCount: 0 },
      { name: "3:4主图(5张)", value: "待生成", source: "AI生成", status: "generate", required: true, type: "image", imageCount: 5, uploadedCount: 0 },
      { name: "白底图", value: "待生成", source: "AI生成", status: "generate", required: true, type: "image", imageCount: 1, uploadedCount: 0 },
      { name: "商品视频", value: "1个待上传", source: "采集", status: "optional", required: false, type: "video", imageCount: 1, uploadedCount: 0 },
      { name: "详情描述", value: "8张待上传", source: "采集", status: "pending", required: true, type: "image", imageCount: 8, uploadedCount: 0 },
    ],
  },
  {
    title: "基础信息",
    icon: <FileText className="h-4 w-4" />,
    fields: [
      { name: "商品标题", value: "有机黑芝麻600g", source: "采集", status: "pending", required: true, type: "text" },
      { name: "品牌", value: "九月的诗", source: "采集+匹配", status: "pending", required: true, type: "text" },
      { name: "系列", value: "有机", source: "采集", status: "completed", required: false, type: "text" },
      { name: "货号", value: "HZM-600G", source: "数据源", status: "completed", required: false, type: "text" },
    ],
  },
  {
    title: "食品安全",
    icon: <Factory className="h-4 w-4" />,
    fields: [
      { name: "厂名", value: "辽宁绿色常兴...", source: "数据源", status: "completed", required: true, type: "text" },
      { name: "厂址", value: "辽宁省铁岭市...", source: "数据源", status: "completed", required: true, type: "text" },
      { name: "厂家联系方式", value: "400-xxx-xxxx", source: "数据源", status: "completed", required: true, type: "text" },
      { name: "生产许可证", value: "SC1234567", source: "模板", status: "completed", required: true, type: "text" },
      { name: "有机编码", value: "2490P1800146", source: "数据源", status: "completed", required: true, type: "text" },
      { name: "配料表", value: "黑芝麻", source: "采集", status: "pending", required: true, type: "text" },
      { name: "保质期", value: "12个月", source: "采集", status: "completed", required: true, type: "text" },
      { name: "储存方法", value: "阴凉干燥处", source: "采集", status: "completed", required: false, type: "text" },
    ],
  },
  {
    title: "物流售后",
    icon: <Truck className="h-4 w-4" />,
    fields: [
      { name: "发货地", value: "浙江杭州", source: "模板", status: "completed", required: true, type: "text" },
      { name: "发货时效", value: "24小时内", source: "模板", status: "completed", required: true, type: "text" },
      { name: "运费模板", value: "包邮模板A", source: "模板", status: "completed", required: true, type: "text" },
      { name: "退换货承诺", value: "7天无理由", source: "模板", status: "completed", required: false, type: "text" },
    ],
  },
];

const statusConfig: Record<FieldStatus, { label: string; color: string }> = {
  completed: { label: "已完成", color: "bg-green-50 text-green-600 border-green-200" },
  pending: { label: "待确认", color: "bg-yellow-50 text-yellow-600 border-yellow-200" },
  generate: { label: "待生成", color: "bg-blue-50 text-blue-600 border-blue-200" },
  optional: { label: "可选", color: "bg-gray-50 text-gray-500 border-gray-200" },
  uploading: { label: "上传中", color: "bg-orange-50 text-orange-600 border-orange-200" },
};

// 树形目录组件
function FolderTree({
  nodes,
  selectedId,
  onSelect,
  expandedIds,
  onToggleExpand,
  level = 0,
}: {
  nodes: FolderNode[];
  selectedId: string;
  onSelect: (id: string, name: string) => void;
  expandedIds: Set<string>;
  onToggleExpand: (id: string) => void;
  level?: number;
}) {
  return (
    <div className="space-y-0.5">
      {nodes.map((node) => {
        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = expandedIds.has(node.id);
        const isSelected = selectedId === node.id;

        return (
          <div key={node.id}>
            <div
              className={cn(
                "flex items-center gap-1 py-1.5 px-2 rounded-lg cursor-pointer transition-colors",
                isSelected ? "bg-blue-100 text-blue-700" : "hover:bg-gray-100"
              )}
              style={{ paddingLeft: `${level * 16 + 8}px` }}
              onClick={() => {
                if (hasChildren) {
                  onToggleExpand(node.id);
                }
                onSelect(node.id, node.name);
              }}
            >
              {hasChildren ? (
                <ChevronRight
                  className={cn(
                    "h-4 w-4 text-gray-400 transition-transform flex-shrink-0",
                    isExpanded && "rotate-90"
                  )}
                />
              ) : (
                <span className="w-4" />
              )}
              {isExpanded ? (
                <FolderOpen className={cn("h-4 w-4 flex-shrink-0", isSelected ? "text-blue-500" : "text-yellow-500")} />
              ) : (
                <Folder className={cn("h-4 w-4 flex-shrink-0", isSelected ? "text-blue-500" : "text-yellow-500")} />
              )}
              <span className={cn("text-sm truncate", isSelected && "font-medium")}>
                {node.name}
              </span>
            </div>
            {hasChildren && isExpanded && (
              <FolderTree
                nodes={node.children!}
                selectedId={selectedId}
                onSelect={onSelect}
                expandedIds={expandedIds}
                onToggleExpand={onToggleExpand}
                level={level + 1}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// 获取文件夹路径
function getFolderPath(nodes: FolderNode[], targetId: string, path: string[] = []): string[] | null {
  for (const node of nodes) {
    if (node.id === targetId) {
      return [...path, node.name];
    }
    if (node.children) {
      const result = getFolderPath(node.children, targetId, [...path, node.name]);
      if (result) return result;
    }
  }
  return null;
}

export default function UploadStep3() {
  const [fieldGroups, setFieldGroups] = useState<FieldGroup[]>(initialFieldGroups);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(
    fieldGroups.map((g) => g.title)
  );
  const [filter, setFilter] = useState<"all" | "required" | FieldStatus>("all");

  // 素材库相关状态
  const [selectedFolderId, setSelectedFolderId] = useState<string>("grain-4");
  const [selectedFolderName, setSelectedFolderName] = useState<string>("黑芝麻(熟)600g");
  const [showFolderPicker, setShowFolderPicker] = useState(false);
  const [expandedFolderIds, setExpandedFolderIds] = useState<Set<string>>(
    new Set(["product", "organic-grain"])
  );
  const [uploadingFields, setUploadingFields] = useState<Set<string>>(new Set());

  const folderPath = getFolderPath(materialFolderTree, selectedFolderId);

  const toggleGroup = (title: string) => {
    setExpandedGroups((prev) =>
      prev.includes(title) ? prev.filter((t) => t !== title) : [...prev, title]
    );
  };

  const toggleFolderExpand = (id: string) => {
    setExpandedFolderIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleSelectFolder = (id: string, name: string) => {
    setSelectedFolderId(id);
    setSelectedFolderName(name);
  };

  // 模拟上传图片到素材库
  const handleUploadToMaterial = (groupTitle: string, fieldName: string) => {
    const fieldKey = `${groupTitle}-${fieldName}`;
    setUploadingFields((prev) => new Set(prev).add(fieldKey));

    setFieldGroups((prev) =>
      prev.map((group) => ({
        ...group,
        fields: group.fields.map((field) =>
          group.title === groupTitle && field.name === fieldName
            ? { ...field, status: "uploading" as FieldStatus }
            : field
        ),
      }))
    );

    setTimeout(() => {
      setUploadingFields((prev) => {
        const next = new Set(prev);
        next.delete(fieldKey);
        return next;
      });

      setFieldGroups((prev) =>
        prev.map((group) => ({
          ...group,
          fields: group.fields.map((field) =>
            group.title === groupTitle && field.name === fieldName
              ? {
                  ...field,
                  status: "completed" as FieldStatus,
                  uploadedCount: field.imageCount,
                  value: `已上传 ${field.imageCount} 张`,
                }
              : field
          ),
        }))
      );
    }, 2000);
  };

  const handleUploadAll = () => {
    fieldGroups.forEach((group) => {
      group.fields.forEach((field) => {
        if ((field.type === "image" || field.type === "video") && field.status !== "completed" && field.status !== "generate") {
          handleUploadToMaterial(group.title, field.name);
        }
      });
    });
  };

  // 统计
  const allFields = fieldGroups.flatMap((g) => g.fields);
  const stats = {
    total: allFields.length,
    required: allFields.filter((f) => f.required).length,
    requiredCompleted: allFields.filter((f) => f.required && f.status === "completed").length,
    completed: allFields.filter((f) => f.status === "completed").length,
    pending: allFields.filter((f) => f.status === "pending").length,
    generate: allFields.filter((f) => f.status === "generate").length,
    optional: allFields.filter((f) => f.status === "optional").length,
    imageFields: allFields.filter((f) => f.type === "image" || f.type === "video").length,
    imageUploaded: allFields.filter((f) => (f.type === "image" || f.type === "video") && f.status === "completed").length,
  };

  const requiredIncomplete = stats.required - stats.requiredCompleted;

  const filterField = (field: Field) => {
    if (filter === "all") return true;
    if (filter === "required") return field.required;
    return field.status === filter;
  };

  return (
    <UploadLayout
      step={3}
      title="确认字段"
      prevHref="/upload/step2"
      nextHref="/upload/step4"
      nextDisabled={requiredIncomplete > 0}
    >
      <div className="space-y-4">
        {/* 必填项警告 */}
        {requiredIncomplete > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div>
              <div className="font-medium text-red-700">
                还有 {requiredIncomplete} 个必填项未完成
              </div>
              <div className="text-sm text-red-600 mt-1">
                请完成所有必填项后才能进入下一步
              </div>
            </div>
          </div>
        )}

        {/* 图片上传到素材库 */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-blue-500" />
              <span className="font-medium text-blue-700">上传图片到千牛素材库</span>
              <Badge className="bg-blue-100 text-blue-600 border-0">
                {stats.imageUploaded}/{stats.imageFields} 已上传
              </Badge>
            </div>
          </div>

          {/* 目录选择 */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-blue-600 flex-shrink-0">目标目录：</span>
            <div className="relative flex-1">
              <button
                onClick={() => setShowFolderPicker(!showFolderPicker)}
                className="flex items-center gap-2 px-3 py-2 bg-white border border-blue-200 rounded-lg text-sm hover:border-blue-300 transition-colors w-full justify-between"
              >
                <span className="flex items-center gap-2 truncate">
                  <FolderOpen className="h-4 w-4 text-yellow-500 flex-shrink-0" />
                  <span className="text-gray-600 truncate">
                    {folderPath ? folderPath.join(" / ") : selectedFolderName}
                  </span>
                </span>
                <ChevronDown className={cn(
                  "h-4 w-4 text-gray-400 transition-transform flex-shrink-0",
                  showFolderPicker && "rotate-180"
                )} />
              </button>

              {/* 树形目录选择器 */}
              {showFolderPicker && (
                <div className="absolute top-full left-0 mt-1 w-80 bg-white border rounded-xl shadow-lg z-20 max-h-80 overflow-auto">
                  <div className="p-3 border-b sticky top-0 bg-white">
                    <div className="text-xs text-gray-500 mb-2">选择素材库目录</div>
                    <FolderTree
                      nodes={materialFolderTree}
                      selectedId={selectedFolderId}
                      onSelect={(id, name) => {
                        handleSelectFolder(id, name);
                        setShowFolderPicker(false);
                      }}
                      expandedIds={expandedFolderIds}
                      onToggleExpand={toggleFolderExpand}
                    />
                  </div>
                  <div className="p-2 border-t bg-gray-50">
                    <button className="text-sm text-blue-500 hover:text-blue-600 font-medium flex items-center gap-1 px-2 py-1">
                      <Plus className="h-3.5 w-3.5" />
                      新建目录
                    </button>
                  </div>
                </div>
              )}
            </div>

            <Button
              onClick={handleUploadAll}
              size="sm"
              className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex-shrink-0"
              disabled={stats.imageUploaded === stats.imageFields}
            >
              <Upload className="h-4 w-4 mr-2" />
              一键上传
            </Button>
          </div>

          <div className="text-xs text-blue-600">
            图片将上传至：千牛 → 店铺 → 素材库 → {folderPath ? folderPath.join(" → ") : selectedFolderName}
          </div>
        </div>

        {/* Filter & Actions */}
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {[
              { key: "all", label: "全部" },
              { key: "required", label: `必填项 (${stats.required})` },
              { key: "pending", label: `待确认 (${stats.pending})` },
              { key: "generate", label: `待生成 (${stats.generate})` },
            ].map((item) => (
              <button
                key={item.key}
                onClick={() => setFilter(item.key as any)}
                className={cn(
                  "px-4 py-1.5 rounded-lg text-sm transition-colors",
                  filter === item.key
                    ? "bg-orange-50 text-orange-600 font-medium"
                    : "text-gray-500 hover:bg-gray-50"
                )}
              >
                {item.label}
              </button>
            ))}
          </div>
          <Button variant="outline" size="sm" className="rounded-lg">
            <Sparkles className="h-4 w-4 mr-2 text-orange-500" />
            一键生成图片
          </Button>
        </div>

        {/* Field Groups */}
        <div className="space-y-3">
          {fieldGroups.map((group) => {
            const filteredFields = group.fields.filter(filterField);
            const groupRequiredIncomplete = group.fields.filter(
              (f) => f.required && f.status !== "completed"
            ).length;

            if (filteredFields.length === 0) return null;

            return (
              <div key={group.title} className="border rounded-xl overflow-hidden">
                <div
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleGroup(group.title)}
                >
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-orange-50 rounded-lg text-orange-500">
                      {group.icon}
                    </div>
                    <span className="font-medium text-gray-800">{group.title}</span>
                    <Badge className="bg-gray-100 text-gray-500 border-0">
                      {group.fields.length}
                    </Badge>
                    {groupRequiredIncomplete > 0 && (
                      <Badge className="bg-red-50 text-red-600 border-red-200">
                        {groupRequiredIncomplete} 必填待完成
                      </Badge>
                    )}
                  </div>
                  {expandedGroups.includes(group.title) ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </div>

                {expandedGroups.includes(group.title) && (
                  <div className="border-t">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="text-left p-3 font-medium text-gray-600">字段</th>
                          <th className="text-left p-3 font-medium text-gray-600">值</th>
                          <th className="text-left p-3 font-medium text-gray-600">来源</th>
                          <th className="text-left p-3 font-medium text-gray-600">状态</th>
                          <th className="text-left p-3 font-medium text-gray-600 w-24">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredFields.map((field, idx) => {
                          const fieldKey = `${group.title}-${field.name}`;
                          const isUploading = uploadingFields.has(fieldKey);
                          const isImageField = field.type === "image" || field.type === "video";

                          return (
                            <tr
                              key={idx}
                              className={cn(
                                "border-t hover:bg-gray-50",
                                field.required && field.status !== "completed" && "bg-red-50/30"
                              )}
                            >
                              <td className="p-3">
                                <div className="flex items-center gap-2">
                                  <span className="text-gray-800">{field.name}</span>
                                  {field.required && (
                                    <span className="text-red-500 font-bold">*</span>
                                  )}
                                  {isImageField && (
                                    <Badge className="bg-purple-50 text-purple-600 border-0 text-xs">
                                      {field.type === "video" ? "视频" : "图片"}
                                    </Badge>
                                  )}
                                </div>
                              </td>
                              <td className="p-3 text-gray-500">{field.value}</td>
                              <td className="p-3">
                                <Badge className="bg-gray-50 text-gray-500 border-gray-200">
                                  {field.source}
                                </Badge>
                              </td>
                              <td className="p-3">
                                <Badge className={cn("border", statusConfig[field.status].color)}>
                                  {field.status === "uploading" && (
                                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                  )}
                                  {statusConfig[field.status].label}
                                </Badge>
                              </td>
                              <td className="p-3">
                                {isImageField && field.status !== "completed" && field.status !== "generate" && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleUploadToMaterial(group.title, field.name);
                                    }}
                                    disabled={isUploading}
                                    className="h-7 text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-50"
                                  >
                                    {isUploading ? (
                                      <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                      <>
                                        <Upload className="h-3 w-3 mr-1" />
                                        上传
                                      </>
                                    )}
                                  </Button>
                                )}
                                {isImageField && field.status === "completed" && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-7 text-xs text-gray-400 hover:text-gray-600"
                                  >
                                    <RefreshCw className="h-3 w-3 mr-1" />
                                    重传
                                  </Button>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-500">
          <div className="flex items-center justify-between">
            <span>
              必填项：
              <span className={cn(
                "font-medium ml-1",
                stats.requiredCompleted === stats.required ? "text-green-600" : "text-red-600"
              )}>
                {stats.requiredCompleted}/{stats.required}
              </span>
              <span className="mx-2">|</span>
              素材上传：
              <span className="font-medium ml-1 text-blue-600">
                {stats.imageUploaded}/{stats.imageFields}
              </span>
              <span className="mx-2">|</span>
              已完成 {stats.completed} / 待确认 {stats.pending} / 待生成 {stats.generate}
            </span>
          </div>
        </div>
      </div>
    </UploadLayout>
  );
}
