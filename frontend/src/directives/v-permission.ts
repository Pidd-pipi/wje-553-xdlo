import type { App, DirectiveBinding } from 'vue';
import { useAuthStore } from '../stores/authStore';
export default { install(app: App) { app.directive('permission', { mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) { const required = Array.isArray(binding.value) ? binding.value : [binding.value]; const auth = useAuthStore(); const normalized = required.map(v => v.toUpperCase()); if (!auth.user || !normalized.includes(auth.user.role)) el.remove(); } }); } };
