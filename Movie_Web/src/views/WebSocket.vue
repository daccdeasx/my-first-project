<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
const ws = ref(null);
const newNotification = ref(null);

onMounted(() => {
  const token = localStorage.getItem('authToken');
  ws.value = new WebSocket(`ws://${window.location.host}/ws/notifications/?token=${token}`);
  
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    newNotification.value = data;
    // 更新通知列表
    loadNotifications();
  };
});

onUnmounted(() => {
  ws.value?.close();
});
</script>