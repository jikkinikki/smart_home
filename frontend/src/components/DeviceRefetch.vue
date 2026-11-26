<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { applyRefetch, getRefetch, startRefetch } from '@/api/DeviceRefetchApi';
import type { DeviceChange, RefetchStatus } from '@/types/DeviceRefetch';

// Tells the page the database changed, so it can load the devices again
const emit = defineEmits<{
    applied: []
}>();

const status = ref<RefetchStatus | null>(null);
const error = ref<string | null>(null);
const message = ref<string | null>(null);

// The devices whose changes will be applied. All of them by default.
const selected = ref(new Set<string>());

const now = ref(Date.now());
let pollTimer: ReturnType<typeof setInterval> | undefined;

const isRunning = computed(() => status.value?.state == "running");
const changes = computed(() => status.value?.state == "done" ? status.value.changes : []);

const secondsWaited = computed(() => {

    const startedAt = status.value?.started_at;
    return startedAt ? Math.max(0, Math.round(now.value / 1000 - startedAt)) : 0;
});

function setStatus(newStatus: RefetchStatus) {

    // Select every change when the result first comes in
    if (newStatus.state == "done" && status.value?.state != "done") {
        selected.value = new Set(newStatus.changes.map(change => change.id));
    }

    status.value = newStatus;

    if (newStatus.state == "running") {
        startPolling();
    }
    else {
        stopPolling();
    }
}

function startPolling() {

    if (pollTimer) return;

    pollTimer = setInterval(async () => {

        now.value = Date.now();

        try {
            setStatus(await getRefetch());
        }
        catch (e) {
            error.value = e instanceof Error ? e.message : String(e);
        }
    }, 1000);
}

function stopPolling() {

    clearInterval(pollTimer);
    pollTimer = undefined;
}

async function refetch() {

    error.value = null;
    message.value = null;
    now.value = Date.now();

    try {
        setStatus(await startRefetch());
    }
    catch (e) {
        error.value = e instanceof Error ? e.message : String(e);
    }
}

function toggle(change: DeviceChange) {

    const newSelected = new Set(selected.value);

    if (!newSelected.delete(change.id)) {
        newSelected.add(change.id);
    }

    selected.value = newSelected;
}

async function apply() {

    error.value = null;

    try {
        const result = await applyRefetch([...selected.value]);
        message.value = `Applied ${result.applied} device(s). Restarting devices...`;
        setStatus(await getRefetch());
        emit("applied");
    }
    catch (e) {
        error.value = e instanceof Error ? e.message : String(e);
    }
}

function formatValue(value: unknown) {

    if (value == null) return "-";
    return typeof value == "object" ? JSON.stringify(value) : String(value);
}

// A fetch might already be running (or done) from before the page was opened
onMounted(async () => {

    try {
        setStatus(await getRefetch());
    }
    catch (e) {
        error.value = e instanceof Error ? e.message : String(e);
    }
});

onUnmounted(stopPolling);

</script>

<template>

    <div class="refetch">

        <button class="refetch-btn" :disabled="isRunning" @click="refetch">
            {{ isRunning ? `Fetching devices... ${secondsWaited}s` : "Refetch devices" }}
        </button>

        <p v-if="isRunning" class="hint">Scanning Tuya and Zigbee devices. This can take a minute or two.</p>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="message">{{ message }}</p>

        <template v-if="status?.state == 'done'">

            <p v-for="(sourceError, source) in status.errors" :key="source" class="error">
                {{ source }} failed: {{ sourceError }}
            </p>

            <p v-if="changes.length == 0">No new or changed devices found.</p>

            <div class="changes">

                <div v-for="change in changes" :key="change.id" class="change"
                    :class="{ unselected: !selected.has(change.id) }" @click="toggle(change)">

                    <div class="change-header">
                        <input type="checkbox" :checked="selected.has(change.id)" @click.stop="toggle(change)">
                        <h3>{{ change.name || "(no name)" }}</h3>
                        <span class="badge" :class="change.status">{{ change.status }}</span>
                    </div>

                    <p class="id">{{ change.source }} · {{ change.id }}</p>

                    <p v-for="field in change.fields" :key="field.field" class="field">
                        <span class="field-name">{{ field.field }}:</span>
                        {{ formatValue(field.old) }} → {{ formatValue(field.new) }}
                    </p>

                </div>

            </div>

            <button v-if="changes.length > 0" class="apply-btn" :disabled="selected.size == 0" @click="apply">
                Apply ({{ selected.size }})
            </button>

        </template>

    </div>

</template>

<style lang="scss" scoped>
.refetch {

    display: flex;
    flex-direction: column;
    gap: 6px;

    p {
        margin: 0;
    }

    button {
        padding: 8px;
    }

    button:disabled {
        opacity: 0.6;
    }

    .hint {
        opacity: 0.6;
    }

    .error {
        color: rgb(240, 110, 110);
    }

    .changes {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 5px;
    }

    .change {

        border: 2px solid var(--button-col);
        padding: 8px;
        cursor: pointer;
        overflow: hidden;

        &.unselected {
            opacity: 0.4;
        }
    }

    .change-header {

        display: flex;
        align-items: center;
        gap: 6px;

        h3 {
            margin: 0;
            flex: 1;
        }
    }

    .badge {

        font-size: 0.8em;
        padding: 2px 6px;
        border-radius: 4px;
        color: rgb(15, 15, 15);

        &.new {
            background-color: rgb(120, 200, 120);
        }

        &.changed {
            background-color: orange;
        }
    }

    .id {
        font-size: 0.8em;
        opacity: 0.6;
        word-break: break-all;
    }

    .field {
        font-size: 0.9em;
        word-break: break-all;
    }

    .field-name {
        opacity: 0.7;
    }
}
</style>
