"use client";

import { useParams } from "next/navigation";
import { EditPlanLayout } from "@/components/edit-plan/EditPlanLayout";

export default function EditPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  return <EditPlanLayout projectId={projectId} />;
}
