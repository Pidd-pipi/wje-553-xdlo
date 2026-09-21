<script setup lang="ts">
import { computed } from 'vue';
const props = withDefaults(defineProps<{ score?: number; totalScore?: number; showBar?: boolean }>(), { totalScore: 100, showBar: false });
const percent = computed(() => props.score == null ? 0 : Math.round(props.score / props.totalScore * 100));
const color = computed(() => percent.value >= 90 ? '#1f9d66' : percent.value >= 60 ? '#2563eb' : '#d92d20');
</script><template><div class="score"><strong :style="{ color }">{{ score == null ? '未评分' : score }}</strong><span>/{{ totalScore }}</span><el-progress v-if="showBar" :percentage="percent" :color="color" :show-text="false" /></div></template><style scoped>.score{display:grid;gap:4px;min-width:96px}.score strong{font-size:18px}</style>