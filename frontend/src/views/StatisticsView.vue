<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NButton, NCard, NGrid, NGridItem, NSpace, NList, NListItem, NSkeleton, NSpin } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { fetchStatistics } from '@/api/machines'
import type { StatisticsData } from '@/types/machine'

const router = useRouter()
const message = useMessage()

const initialState: StatisticsData = {
  total_machines: 0,
  operational_count: 0,
  out_of_service_count: 0,
  location_distribution: [],
  category_rankings: [],
}

const isReady = ref(false)

const {
  state: statistics,
  isLoading,
  execute: reload,
} = useAsyncState<StatisticsData>(
  async () => {
    try {
      const result = await fetchStatistics()
      isReady.value = true
      return result
    } catch {
      message.error('加载统计数据失败')
      isReady.value = true
      return {
        total_machines: 0,
        operational_count: 0,
        out_of_service_count: 0,
        location_distribution: [],
        category_rankings: [],
      }
    }
  },
  initialState,
  { immediate: false, resetOnExecute: false },
)

const maxLocationCount = computed(() => {
  if (!statistics.value.location_distribution.length) return 1
  return Math.max(...statistics.value.location_distribution.map((l) => l.count))
})

const maxCategoryCount = computed(() => {
  if (!statistics.value.category_rankings.length) return 1
  return Math.max(...statistics.value.category_rankings.map((c) => c.count))
})

function getBarWidth(count: number, max: number): string {
  if (max === 0) return '0%'
  return `${(count / max) * 100}%`
}

async function handleRefresh() {
  isReady.value = false
  await reload()
}

onMounted(() => {
  reload()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>数据统计看板</h1>
        <p class="subtitle">售货机运营数据汇总分析</p>
      </div>
      <NSpace>
        <NButton @click="router.push('/')">返回列表</NButton>
        <NButton type="primary" :loading="isLoading" @click="handleRefresh">刷新数据</NButton>
      </NSpace>
    </header>

    <NSpin :show="isLoading && !isReady" :stroke-width="18">
      <NGrid :x-gap="20" :y-gap="20" :cols="3" class="stats-cards">
        <NGridItem>
          <NCard class="stat-card stat-card-total">
            <template v-if="!isReady">
              <NSkeleton animated width="56" height="56" circle />
              <div class="stat-content">
                <NSkeleton animated text style="width: 100px" />
                <NSkeleton animated text style="width: 80px; height: 36px" />
              </div>
            </template>
            <template v-else>
              <div class="stat-icon">📦</div>
              <div class="stat-content">
                <div class="stat-label">售货机总数</div>
                <div class="stat-value">{{ statistics.total_machines }}</div>
              </div>
            </template>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard class="stat-card stat-card-operational">
            <template v-if="!isReady">
              <NSkeleton animated width="56" height="56" circle />
              <div class="stat-content">
                <NSkeleton animated text style="width: 80px" />
                <NSkeleton animated text style="width: 80px; height: 36px" />
              </div>
            </template>
            <template v-else>
              <div class="stat-icon">✅</div>
              <div class="stat-content">
                <div class="stat-label">运作中</div>
                <div class="stat-value">{{ statistics.operational_count }}</div>
              </div>
            </template>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard class="stat-card stat-card-out">
            <template v-if="!isReady">
              <NSkeleton animated width="56" height="56" circle />
              <div class="stat-content">
                <NSkeleton animated text style="width: 80px" />
                <NSkeleton animated text style="width: 80px; height: 36px" />
              </div>
            </template>
            <template v-else>
              <div class="stat-icon">⚠️</div>
              <div class="stat-content">
                <div class="stat-label">已停运</div>
                <div class="stat-value">{{ statistics.out_of_service_count }}</div>
              </div>
            </template>
          </NCard>
        </NGridItem>
      </NGrid>

      <NGrid :x-gap="20" :y-gap="20" :cols="1" :l-cols="2" class="stats-charts">
        <NGridItem>
          <NCard title="地点分布汇总" class="chart-card">
            <template v-if="!isReady">
              <div class="skeleton-list">
                <div v-for="i in 5" :key="i" class="skeleton-item">
                  <div class="skeleton-item-row">
                    <NSkeleton animated text style="width: 180px" />
                    <NSkeleton animated text style="width: 60px" />
                  </div>
                  <NSkeleton animated style="height: 8px; width: 100%; border-radius: 4px" />
                </div>
              </div>
            </template>
            <template v-else>
              <div v-if="!statistics.location_distribution.length" class="empty-state">
                暂无数据
              </div>
              <NList v-else bordered class="stats-list">
                <NListItem v-for="loc in statistics.location_distribution" :key="loc.location">
                  <div class="list-item-content">
                    <span class="item-name">{{ loc.location }}</span>
                    <span class="item-count">{{ loc.count }} 台</span>
                  </div>
                  <div class="bar-container">
                    <div
                      class="bar bar-location"
                      :style="{ width: getBarWidth(loc.count, maxLocationCount) }"
                    />
                  </div>
                </NListItem>
              </NList>
            </template>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard title="售卖品类排行" class="chart-card">
            <template v-if="!isReady">
              <div class="skeleton-list">
                <div v-for="i in 5" :key="i" class="skeleton-item">
                  <div class="skeleton-item-row">
                    <NSkeleton animated width="24" height="24" circle />
                    <NSkeleton animated text style="width: 160px" />
                    <NSkeleton animated text style="width: 60px" />
                  </div>
                  <NSkeleton animated style="height: 8px; width: 100%; border-radius: 4px" />
                </div>
              </div>
            </template>
            <template v-else>
              <div v-if="!statistics.category_rankings.length" class="empty-state">
                暂无数据
              </div>
              <NList v-else bordered class="stats-list">
                <NListItem v-for="(cat, index) in statistics.category_rankings" :key="cat.category">
                  <div class="list-item-content">
                    <span class="item-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
                    <span class="item-name">{{ cat.category }}</span>
                    <span class="item-count">{{ cat.count }} 次</span>
                  </div>
                  <div class="bar-container">
                    <div
                      class="bar bar-category"
                      :style="{ width: getBarWidth(cat.count, maxCategoryCount) }"
                    />
                  </div>
                </NListItem>
              </NList>
            </template>
          </NCard>
        </NGridItem>
      </NGrid>
    </NSpin>
  </div>
</template>

<style scoped>
.page {
  max-width: 1300px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: 1.75rem;
  color: #3d2f1f;
}

.subtitle {
  margin: 0;
  color: #7a6a55;
  font-size: 0.95rem;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fffdf8;
  border: 1px solid #e8dcc8;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(61, 47, 31, 0.12);
}

.stat-card-total {
  border-left: 4px solid #18a058;
}

.stat-card-operational {
  border-left: 4px solid #2080f0;
}

.stat-card-out {
  border-left: 4px solid #f0a020;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-content {
  flex: 1;
}

.stat-label {
  color: #7a6a55;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #3d2f1f;
}

.stats-charts {
  margin-bottom: 24px;
}

.chart-card {
  background: #fffdf8;
  border: 1px solid #e8dcc8;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.stats-list {
  margin-top: 16px;
}

.list-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.item-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e8dcc8;
  color: #7a6a55;
  font-size: 0.8rem;
  font-weight: 600;
  flex-shrink: 0;
}

.rank-1 {
  background: #ffd700;
  color: #8b6914;
}

.rank-2 {
  background: #c0c0c0;
  color: #5a5a5a;
}

.rank-3 {
  background: #cd7f32;
  color: #fff;
}

.item-name {
  flex: 1;
  font-weight: 500;
  color: #3d2f1f;
}

.item-count {
  color: #7a6a55;
  font-size: 0.9rem;
  font-weight: 600;
  flex-shrink: 0;
}

.bar-container {
  height: 8px;
  background: #f0e8d8;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar-location {
  background: linear-gradient(90deg, #2080f0, #63b3ed);
}

.bar-category {
  background: linear-gradient(90deg, #18a058, #36d399);
}

.skeleton-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-item-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
