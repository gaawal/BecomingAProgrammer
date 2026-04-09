<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from './api'

const USER_ID = 'u1001'
const TEAM_ID = 'team-a'

const loading = ref(true)
const error = ref('')
const user = ref(null)
const tasks = ref([])
const team = ref(null)
const rewards = ref([])
const toast = ref('')

const levelProgress = computed(() => {
  if (!user.value) return 0
  const thresholds = [0, 200, 500, 900, 1400]
  const current = user.value.points
  const lv = user.value.level
  const start = thresholds[lv - 1] ?? 0
  const end = thresholds[lv] ?? start + 500
  return Math.min(100, Math.round(((current - start) / (end - start)) * 100))
})

const fetchAll = async () => {
  loading.value = true
  error.value = ''
  try {
    const [u, t, tm, rw] = await Promise.all([
      api.getUser(USER_ID),
      api.getTasks(USER_ID),
      api.getTeam(TEAM_ID),
      api.getRewards()
    ])
    user.value = u
    tasks.value = t
    team.value = tm
    rewards.value = rw
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const completeTask = async (taskId) => {
  try {
    await api.completeTask(taskId)
    toast.value = '任务完成，积分到账 + 伙伴状态已刷新'
    await fetchAll()
  } catch (e) {
    toast.value = `任务提交失败：${e.message}`
  }
}

const redeem = async (rewardId) => {
  try {
    await api.redeem(USER_ID, rewardId)
    toast.value = '兑换成功，已同步到奖励记录'
    await fetchAll()
  } catch (e) {
    toast.value = `兑换失败：${e.message}`
  }
}

onMounted(fetchAll)
</script>

<template>
  <main class="layout">
    <header class="hero">
      <h1>程序员职场养成系统 · MVP</h1>
      <p>工作完成 → 积分增长 → 伙伴升级 → 奖励解锁</p>
    </header>

    <p v-if="toast" class="toast">{{ toast }}</p>
    <p v-if="error" class="error">错误：{{ error }}</p>

    <section v-if="loading" class="card">加载中...</section>

    <template v-else>
      <section class="grid">
        <article class="card">
          <h2>个人养成主页</h2>
          <p><strong>{{ user.name }}</strong> · {{ user.department }} · {{ user.title }}</p>
          <p>虚拟伙伴：{{ user.partner.name }}（{{ user.partner.status }}）</p>
          <p>积分：{{ user.points }} · 等级：Lv.{{ user.level }}</p>
          <div class="progress">
            <div class="bar" :style="{ width: `${levelProgress}%` }" />
          </div>
          <p>技术树：{{ user.tech_tree.join(' / ') }}</p>
        </article>

        <article class="card">
          <h2>工作任务对接</h2>
          <ul class="list">
            <li v-for="task in tasks" :key="task.id" class="row">
              <div>
                <p class="task-title">{{ task.title }}</p>
                <p class="meta">{{ task.project }} · 难度 {{ task.difficulty }} · {{ task.status }}</p>
              </div>
              <button :disabled="task.status === 'done'" @click="completeTask(task.id)">
                {{ task.status === 'done' ? '已完成' : '完成任务' }}
              </button>
            </li>
          </ul>
        </article>
      </section>

      <section class="grid">
        <article class="card">
          <h2>团队协作养成</h2>
          <p><strong>{{ team.name }}</strong> · 排名 #{{ team.rank }}</p>
          <p>团队积分：{{ team.points }}</p>
          <p>团队成就：{{ team.unlocked.join('、') }}</p>
          <p>成员：{{ team.members.map((m) => m.name).join('、') }}</p>
        </article>

        <article class="card">
          <h2>成就与奖励</h2>
          <ul class="list">
            <li v-for="reward in rewards" :key="reward.id" class="row">
              <div>
                <p class="task-title">{{ reward.name }}</p>
                <p class="meta">消耗 {{ reward.cost }} 分 · 库存 {{ reward.stock }}</p>
              </div>
              <button :disabled="reward.stock === 0" @click="redeem(reward.id)">兑换</button>
            </li>
          </ul>
        </article>
      </section>
    </template>
  </main>
</template>
