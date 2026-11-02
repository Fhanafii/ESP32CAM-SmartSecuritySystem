"use client";

import Link from "next/link";
import { useState } from "react";
import {
    Card,
    CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Detection } from "@/types/detection";
import { getStatusBadgeClass } from "@/lib/status";

interface Props{
    detection:Detection;
}

export function HistoryCard({
    detection,
}:Props){
    const [imageFailed, setImageFailed] = useState(false);

    return(
        <Link href={`/detections/${detection.id}`}>

            <Card className="cursor-pointer transition hover:shadow-md">

                <CardContent className="flex items-center gap-4 p-4">

                    <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-muted">
                        {detection.preview_image_url && !imageFailed ? (
                            <img
                                src={detection.preview_image_url}
                                alt={`Frame terdeteksi batch #${detection.batch_number}`}
                                className="h-full w-full object-cover"
                                loading="lazy"
                                onError={() => setImageFailed(true)}
                            />
                        ) : (
                            <span className="px-1 text-center text-xs text-muted-foreground">
                                No Image
                            </span>
                        )}
                    </div>

                    <div className="flex-1">

                        <h3 className="font-semibold">
                            Batch #{detection.batch_number}
                        </h3>

                        <p className="text-sm text-muted-foreground">

                            {new Date(detection.detected_at)
                                .toLocaleString("id-ID")}
                        </p>

                        <p className="mt-2 text-sm">
                            Confidence
                            {" "}
                            {(detection.avg_confidence)}%
                        </p>
                    </div>

                    <Badge className={getStatusBadgeClass(detection.status)}>
                        {detection.status}
                    </Badge>
                </CardContent>
            </Card>
        </Link>
    );
}
