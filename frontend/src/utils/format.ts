export function formatDate(value?: string) { return value ? new Date(value).toLocaleDateString('zh-CN') : '-'; }
export function formatScore(score?: number, total?: number) { return score == null ? '未评分' : total ? score + '/' + total : String(score); }
