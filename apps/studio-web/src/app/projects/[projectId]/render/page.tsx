"use client";

import { useParams } from "next/navigation";
import { RenderQueueLayout } from "@/components/render/RenderQueueLayout";

export default function RenderPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  return <RenderQueueLayout projectId={projectId} />;
}
