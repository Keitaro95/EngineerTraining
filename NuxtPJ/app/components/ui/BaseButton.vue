<script lang="ts" setup>
import type { IconName } from '../icon'
import { iconMap } from '../icon/icon.vue'

interface Props {
    type?: 'default' | 'primary' | 'success' | 'info' | 'warning' | 'danger'
    size?: 'small' | 'default' | 'large'
    color?: 'default' | 'navy'
    icon?: IconName
    plain?: boolean
    text?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    type: 'default',
    size: 'default',
    color: 'default',
    plain: false,
    text: false,
    icon: undefined,
})

const buttonColor = computed(() => {
    switch (props.color) {
        case 'navy':
            return '#001A78'
        default:
            return undefined
    }
})

const buttonIcon = computed(() => (props.icon ? iconMap[props.icon] : undefined))
</script>

<template>
    <el-button
        :type="type"
        :size="size"
        :color="buttonColor"
        :plain="plain"
        :text="text"
        :icon="buttonIcon"
    >
        <slot />
    </el-button>
</template>

<style lang="scss" scoped>
.a-button {
    &.el-button {
        :deep([class*='el-icon'] + span) {
            margin-left: 0;
        }

        &.el-button--small {
            padding: 0 11px;
        }
    }
}
</style>