
<script setup lang="ts">
import { computed, ref, type Component } from 'vue'

// Automatically discover all Vue components
const modules = import.meta.glob<{ default: Component }>(
  '../components/**/*.vue',
  { eager: true }
)

const components = Object.entries(modules).map(([path, module]) => ({
  name: path
    .replace('../components/', '')
    .replace(/\.vue$/, ''),
  component: module.default,
}))

const selected = ref(components[0]?.name ?? '')

const activeComponent = computed(
  () => components.find(c => c.name === selected.value)?.component
)
</script>

<template>
  <div class="playground">
    <aside>
      <h3>Components</h3>

      <button
        v-for="item in components"
        :key="item.name"
        @click="selected = item.name"
      >
        {{ item.name }}
      </button>
    </aside>

    <main>
      <h2>{{ selected }}</h2>
      <component :is="activeComponent" v-if="activeComponent" />
    </main>
  </div>
</template>

<style scoped>
.playground {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

aside {
  padding: 20px;
  border-right: 1px solid #ccc;
}

aside button {
  display: block;
  padding: 10px;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

main {
  padding: 30px;
}
</style>
