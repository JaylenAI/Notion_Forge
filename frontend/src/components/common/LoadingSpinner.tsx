export default function LoadingSpinner() {
  return (
    <div className="flex items-center gap-2 text-gray-400">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-500" />
      <span>생성 중...</span>
    </div>
  );
}
