export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-sunken ${className}`} />;
}

export function DocRowSkeleton() {
  return (
    <div className="flex items-center gap-3.5 px-5 py-4">
      <Skeleton className="h-5 w-5 shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-3 w-1/4" />
      </div>
      <Skeleton className="h-6 w-16 rounded-md" />
    </div>
  );
}
