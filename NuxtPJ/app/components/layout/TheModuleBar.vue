<script setup lang="ts">
import type { Menu } from '~/components/molecules'

const router = useRouter()

const handleGoToBlogPage = () => {
    router.push('/blog')
}

const handleGoToContactPage = () => {
    router.push('/contact')
}

const menus: Menu[] = [
    [
        { title: 'ブログ', onClick: handleGoToBlogPage },
        { title: 'お問い合わせ', onClick: handleGoToContactPage }
    ],
]
</script>

<template>
    <div class="o-module-bar">
        <BaseButton v-for="(menu, index) in menus[0]" :key="index" color="navy" @click="menu.onClick">
            {{ menu.title }}
        </BaseButton>
    </div>
</template>

<style lang="scss" scoped>
.o-module-bar {
    padding: 24px;
    color: rgb(0 26 120)
}
</style>