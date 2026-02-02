"use client";

import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface Step {
  id: number;
  title: string;
}

const steps: Step[] = [
  { id: 1, title: "输入链接" },
  { id: 2, title: "选择类目" },
  { id: 3, title: "确认字段" },
  { id: 4, title: "编辑SKU" },
  { id: 5, title: "提交上架" },
];

interface StepIndicatorProps {
  currentStep: number;
}

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-center space-x-2">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center">
          <div className="flex flex-col items-center">
            <div
              className={cn(
                "w-9 h-9 rounded-xl flex items-center justify-center text-sm font-medium transition-colors",
                currentStep > step.id
                  ? "bg-green-500 text-white"
                  : currentStep === step.id
                  ? "bg-gradient-to-br from-orange-400 to-orange-500 text-white shadow-lg shadow-orange-200"
                  : "bg-gray-100 text-gray-400"
              )}
            >
              {currentStep > step.id ? (
                <Check className="h-4 w-4" />
              ) : (
                step.id
              )}
            </div>
            <span
              className={cn(
                "text-xs mt-2",
                currentStep >= step.id
                  ? "text-gray-700 font-medium"
                  : "text-gray-400"
              )}
            >
              {step.title}
            </span>
          </div>
          {index < steps.length - 1 && (
            <div
              className={cn(
                "w-16 h-1 mx-3 rounded-full",
                currentStep > step.id ? "bg-green-500" : "bg-gray-100"
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
}
