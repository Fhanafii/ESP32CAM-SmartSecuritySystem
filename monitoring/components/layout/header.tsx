import { MessageCircle, Search } from "lucide-react";
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
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-2 px-3 sm:gap-4 sm:px-6">

        <div className="flex min-w-0 items-center gap-2 sm:gap-3">
          <Image src="/iotmonitoring.svg" alt="IoT Monitoring" width={40} height={40} className="h-8 w-8 shrink-0 rounded-lg sm:h-10 sm:w-10" />
          <div>
          <h1 className="whitespace-nowrap text-sm font-bold sm:text-xl">
            Monitoring Deteksi
          </h1>

          <p className="hidden text-sm text-muted-foreground sm:block">
            Sistem Keamanan Otomatis Berbasis IoT RT 007
          </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <div className="relative w-24 sm:w-56 lg:w-80">

          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />

          <Input
            placeholder="Cari batch..."
            className="pl-9"
            value={keyword}
            onChange={(e) => onKeywordChange(e.target.value)}
          />

          </div>

          <a
            href="https://www.whatsapp.com/channel/0029VbCl5LWDp2Q8JJ204U1c"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Ikuti WhatsApp Channel"
            title="Ikuti WhatsApp Channel"
            className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-green-600/30 bg-green-600/10 px-2.5 text-sm font-medium text-green-700 transition-colors hover:bg-green-600/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-600 dark:text-green-400 sm:px-3"
          >
            <MessageCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span className="hidden sm:inline">Ikuti WhatsApp Channel</span>
          </a>
        </div>

      </div>
    </header>
  );
}
