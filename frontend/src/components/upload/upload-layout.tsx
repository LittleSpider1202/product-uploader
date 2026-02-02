"use client";

import { MainLayout } from "@/components/layout";
import { StepIndicator } from "./step-indicator";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ArrowRight } from "lucide-react";
import Link from "next/link";

interface UploadLayoutProps {
  step: number;
  title: string;
  children: React.ReactNode;
  onPrev?: () => void;
  onNext?: () => void;
  prevHref?: string;
  nextHref?: string;
  nextLabel?: string;
  nextDisabled?: boolean;
}

export function UploadLayout({
  step,
  title,
  children,
  onPrev,
  onNext,
  prevHref,
  nextHref,
  nextLabel = "下一步",
  nextDisabled = false,
}: UploadLayoutProps) {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Step Indicator */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <StepIndicator currentStep={step} />
        </div>

        {/* Content Card */}
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div className="border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
              <span className="text-sm text-gray-400">
                步骤 {step}/5
              </span>
            </div>
          </div>
          <div className="p-6">{children}</div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <div>
            {step > 1 &&
              (prevHref ? (
                <Link href={prevHref}>
                  <Button variant="outline" className="rounded-xl">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    上一步
                  </Button>
                </Link>
              ) : (
                <Button variant="outline" onClick={onPrev} className="rounded-xl">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  上一步
                </Button>
              ))}
          </div>
          <div>
            {nextHref ? (
              <Link href={nextHref}>
                <Button disabled={nextDisabled} className="btn-primary-gradient rounded-xl px-6">
                  {nextLabel}
                  {nextLabel === "下一步" && (
                    <ArrowRight className="h-4 w-4 ml-2" />
                  )}
                </Button>
              </Link>
            ) : (
              <Button onClick={onNext} disabled={nextDisabled} className="btn-primary-gradient rounded-xl px-6">
                {nextLabel}
                {nextLabel === "下一步" && (
                  <ArrowRight className="h-4 w-4 ml-2" />
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
