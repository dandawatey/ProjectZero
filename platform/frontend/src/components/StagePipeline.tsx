import React from 'react';
import type { WorkflowStep } from '../types/workflow';

const dotColor: Record<string, string> = {
  pending: 'bg-gray-300',
  in_progress: 'bg-blue-500 animate-pulse',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
  skipped: 'bg-gray-200',
};

const lineColor: Record<string, string> = {
  completed: 'bg-green-400',
  failed: 'bg-red-400',
};

interface StagePipelineProps {
  steps: WorkflowStep[];
}

export default function StagePipeline({ steps }: StagePipelineProps) {
  if (!steps.length) return null;

  return (
    <div className="flex items-center gap-0 overflow-x-auto py-4">
      {steps.map((step, i) => (
        <React.Fragment key={step.id}>
          <div className="flex flex-col items-center min-w-[80px]">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${dotColor[step.status] ?? 'bg-gray-300'}`}
            >
              {i + 1}
            </div>
            <span className="mt-1 text-[11px] text-gray-600 text-center leading-tight max-w-[90px] truncate">
              {step.stage_name}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div
              className={`h-0.5 w-8 flex-shrink-0 ${lineColor[step.status] ?? 'bg-gray-200'}`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
