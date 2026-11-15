<script setup lang="ts">

    import placeholderIcon from "@/assets/icons/lights-all.svg";

    type ButtonType = "placeholder"

    const lampIcons: Record<ButtonType, string> = {

        placeholder: placeholderIcon
    }

    const props = withDefaults(defineProps<{
        lampName: string
        icon: ButtonType
    }>(), {
        lampName: "placeholder",
        icon: "placeholder"

    });

    function getLampIcon(){

        return lampIcons[props.icon];
    }

</script>

<template>

    <div class="button-wrapper">

        <div class="icon">

            <img :src="getLampIcon()" alt="">

        </div>

        <p class="lamp-name">{{lampName}}</p>

    </div>

</template>

<style scoped>
.button-wrapper {

    min-width: 100px;

    padding: 10px;
    box-sizing: border-box;

    background-color: var(--button-col);

    border-radius: 15px;

    display: flex;
    align-items: center;
    gap: 6px;

    .icon {

        height: 100%;
        aspect-ratio: 1;
        background-color: orange;
        border-radius: 10000px;

        img{

            --width: 60%;

            margin: calc((100% - var(--width)) / 2);
            width: var(--width);

        }
    }

    .lamp-name {

        margin: 10px 0px;
        display: inline;
    }
}
</style>