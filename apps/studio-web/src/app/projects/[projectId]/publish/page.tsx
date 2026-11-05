"use client";

import { useParams } from "next/navigation";
import { PublishingHub } from "@/components/publish/PublishingHub";

export default function PublishPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  return <PublishingHub projectId={projectId} />;
}
