import { Search } from "lucide-react";
import Image from "next/image";
import { Input } from "@/components/ui/input";

interface HeaderProps {
  keyword: string;
  onKeywordChange: (value: string) => void;
}

export function Header({
  keyword,
  onKeywordChange,
}: HeaderProps) {
  return (
    <header className="border-b bg-background">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

        <div className="flex items-center gap-3">
          <Image src="/iotmonitoring.svg" alt="IoT Monitoring" width={40} height={40} className="rounded-lg" />
          <div>
          <h1 className="text-xl font-bold">
            Monitoring Deteksi
          </h1>

          <p className="text-sm text-muted-foreground">
            Sistem Keamanan Otomatis Berbasis IoT RT 007
          </p>
          </div>
        </div>

        <div className="relative w-80">

          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />

          <Input
            placeholder="Cari batch..."
            className="pl-9"
            value={keyword}
            onChange={(e) => onKeywordChange(e.target.value)}
          />

        </div>

      </div>
    </header>
  );
}