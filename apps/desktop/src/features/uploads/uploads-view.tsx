import { FolderInput } from "lucide-react";

import { FeaturePreview } from "@/components/ui/feature-preview";

export const UploadsView = (): JSX.Element => {
  return (
    <FeaturePreview
      eyebrow="Ingestion"
      title="Source media intake built for reliability and speed"
      description="Upload experiences will support validation, checksum verification, queue-aware intake, and structured media handoff without compromising operator confidence."
      icon={FolderInput}
      bullets={[
        "Drag-and-drop intake with storage policy routing",
        "Checksum validation and duplicate detection",
        "Lifecycle movement across incoming, processing, and completed lanes"
      ]}
    />
  );
};
