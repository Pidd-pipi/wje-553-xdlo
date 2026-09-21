import axios from 'axios';
import { ElMessage } from 'element-plus';
import { storage } from './storage';

export const request = axios.create({ baseURL: '/api', timeout: 10000 });
request.interceptors.request.use((config) => {
  const token = storage.getToken();
  if (token) config.headers.Authorization = 'Bearer ' + token;
  return config;
});
request.interceptors.response.use((res) => res.data, (error) => {
  const status = error.response?.status;
  const detail = error.response?.data?.message || error.message;
  if (status === 401) { storage.clearToken(); location.href = '/login'; }
  else if (status === 403) ElMessage.error('无权限执行此操作');
  else if (status === 404) ElMessage.error('请求的资源不存在');
  else if (status === 422) ElMessage.error('表单校验失败');
  else if (status >= 500) ElMessage.error('服务器内部错误，请稍后重试');
  else ElMessage.error(detail);
  return Promise.reject(error);
});
