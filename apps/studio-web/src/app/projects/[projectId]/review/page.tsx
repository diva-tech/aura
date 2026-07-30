import { Metadata } from "next";
import ReviewLayout from "@/components/review/ReviewLayout";

export const metadata: Metadata = {
  title: "AI Review | AURA Studio",
  description: "Professional AI video review and optimization",
};

interface ReviewPageProps {
  params: {
    projectId: string;
  };
}

export default function ReviewPage({ params }: ReviewPageProps) {
  return <ReviewLayout projectId={params.projectId} />;
}
