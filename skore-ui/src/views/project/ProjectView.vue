<script setup lang="ts">
import { formatDistance } from "date-fns";
import Simplebar from "simplebar-vue";
import { onBeforeUnmount, onMounted, ref } from "vue";

import DraggableList from "@/components/DraggableList.vue";
import MediaWidgetSelector from "@/components/MediaWidgetSelector.vue";
import ProjectViewCard from "@/components/ProjectViewCard.vue";
import SimpleButton from "@/components/SimpleButton.vue";
import { useProjectStore } from "@/stores/project";
import { useToastsStore } from "@/stores/toasts";
import ItemNote from "@/views/project/ItemNote.vue";
import ProjectItemList from "@/views/project/ProjectItemList.vue";
import ProjectViewNavigator from "@/views/project/ProjectViewNavigator.vue";

const props = defineProps({
  showCardActions: {
    type: Boolean,
    default: true,
  },
});

const projectStore = useProjectStore();
const isInFocusMode = ref(false);
const currentDropPosition = ref<number>();
const toastsStore = useToastsStore();

function onFocusMode() {
  isInFocusMode.value = !isInFocusMode.value;
}

function onCardRemoved(key: string) {
  if (projectStore.currentView) {
    projectStore.hideKey(projectStore.currentView, key);
  }
}

function onItemDrop(event: DragEvent) {
  if (projectStore.currentView) {
    if (event.dataTransfer) {
      const itemName = event.dataTransfer.getData("application/x-skore-item-name");
      projectStore.displayKey(projectStore.currentView, itemName, currentDropPosition.value ?? 0);
    }
  } else {
    toastsStore.addToast("No view selected", "error");
  }
}

function getItemSubtitle(created_at: Date) {
  const now = new Date();
  return `Created ${formatDistance(created_at, now)} ago`;
}

onMounted(async () => {
  await projectStore.startBackendPolling();
});

onBeforeUnmount(() => {
  projectStore.stopBackendPolling();
});
</script>

<template>
  <main class="project-view" v-if="projectStore.items !== null">
    <div class="left-panel" v-if="projectStore.items && !isInFocusMode">
      <ProjectItemList />
    </div>
    <div ref="editor" class="editor">
      <div class="editor-header">
        <SimpleButton
          icon="icon-left-double-chevron"
          @click="onFocusMode"
          class="focus-mode-button"
          :class="{ flipped: isInFocusMode }"
        />
        <ProjectViewNavigator />
      </div>
      <Transition name="fade">
        <div
          v-if="
            projectStore.currentView === null ||
            projectStore.views[projectStore.currentView] === undefined ||
            projectStore.views[projectStore.currentView]?.length === 0
          "
          class="placeholder"
          @drop="onItemDrop($event)"
          @dragover.prevent
        >
          <div class="wrapper" v-if="projectStore.currentView === null">No view selected.</div>
          <div class="dropzone" v-else>
            <div class="wrapper">The view is empty, start by dropping an item.</div>
          </div>
        </div>
        <Simplebar class="editor-container" v-else>
          <DraggableList
            v-model:items="projectStore.currentViewItems"
            auto-scroll-container-selector=".editor-container"
            v-model:current-drop-position="currentDropPosition"
            @drop="onItemDrop($event)"
            @dragover.prevent
          >
            <template #item="{ name, mediaType, data, createdAt, updatedAt, updates, note }">
              <ProjectViewCard
                :key="name"
                :title="name"
                :subtitle="getItemSubtitle(createdAt)"
                :showActions="props.showCardActions"
                :updates="updates"
                :current-update-index="projectStore.getCurrentItemUpdateIndex(name)"
                :data-name="name"
                @card-removed="onCardRemoved(name)"
                @update-selected="projectStore.setCurrentItemUpdateIndex(name, $event)"
              >
                <ItemNote :name="name" :note="note" />
                <MediaWidgetSelector :item="{ name, mediaType, data, createdAt, updatedAt }" />
              </ProjectViewCard>
            </template>
          </DraggableList>
        </Simplebar>
      </Transition>
    </div>
  </main>
  <main class="not-found" v-else>No Skore has been created, this worskpace is empty.</main>
</template>

<style scoped>
main {
  display: flex;
  overflow: hidden;
  min-width: 0;
  flex-direction: row;

  &.project-view {
    height: 100dvh;
    flex-direction: row;

    & .left-panel {
      display: flex;
      width: 200px;
      flex-direction: column;
      flex-shrink: 0;
      border-right: solid 1px var(--color-stroke-background-primary);

      & .views-list {
        z-index: 2;
      }

      & .keys-list {
        z-index: 1;
        height: 0;
        flex: 1;
      }
    }

    & .editor {
      --editor-height: 44px;

      display: flex;
      min-width: 0;
      max-height: 100vh;
      flex: auto;
      flex-direction: column;

      & .editor-header {
        display: flex;
        height: var(--editor-height);
        align-items: center;
        padding: var(--spacing-12);
        border-bottom: solid var(--stroke-width-md) var(--color-stroke-background-primary);
        background-color: var(--color-background-secondary);

        & .project-view-navigator {
          flex-grow: 1;
          color: var(--color-text-primary);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-regular);
          text-align: center;
        }

        & .focus-mode-button {
          transform-origin: center;

          &.flipped {
            transform: scaleX(-1);
          }
        }
      }

      & .placeholder {
        display: flex;
        height: 100%;
        flex-direction: column;
        justify-content: center;
        background-color: var(--color-background-primary);
        color: var(--color-text-secondary);

        & .wrapper {
          padding-top: 225px;
          margin: var(--spacing-24);
          background-image: var(--image-editor-placeholder);
          background-position: 50% 0;
          background-repeat: no-repeat;
          background-size: 265px 192px;
          text-align: center;
        }

        & .dropzone {
          display: flex;
          height: 100%;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          border-radius: var(--radius-lg);
          margin: var(--spacing-24);
          background-color: var(--color-background-secondary);
          background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='17' ry='17' stroke='%23BABBBDFF' stroke-width='1' stroke-dasharray='11%2c11' stroke-dashoffset='0' stroke-linecap='square'/%3e%3c/svg%3e");
        }
      }

      & .editor-container {
        height: 0;
        flex: 1;
        padding: var(--spacing-24);

        & .draggable {
          min-height: calc(100dvh - var(--editor-height) - var(--spacing-24) * 2);
          gap: var(--spacing-24);
        }

        & .item-note {
          margin-bottom: var(--spacing-16);
        }
      }
    }
  }

  &.not-found {
    display: flex;
    height: 100vh;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--color-text-secondary);
  }
}
</style>
