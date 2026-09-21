<script setup lang="ts">
const visible = defineModel<boolean>({ default: false });
defineProps<{ title: string; message: string }>();
const emit = defineEmits<{ confirm: [] }>();
</script><template><el-dialog v-model="visible" :title="title" width="360"><p>{{ message }}</p><template #footer><el-button @click="visible=false">取消</el-button><el-button type="danger" @click="emit('confirm'); visible=false">确认</el-button></template></el-dialog></template>