<template>
    <div class="app-layout">
      <!-- 包含App.vue中的导航栏 -->
      <AppNav />
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </template>
  
  <script setup>
  import AppNav from '../components/AppNav.vue'
  </script>
  
  <style>
  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  .main-content {
    flex: 1;
    padding: 2rem;
    background: #f5f5f5;
  }
  </style>