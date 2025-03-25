<!-- src/components/TagBadge.vue -->
<template>
  <q-chip
    :style="`background-color: ${tag.color}10; color: ${tag.color}; border: 1px solid ${tag.color}50;`"
    dense
    class="intelligence-vinculo-badge"
    :removable="removable"
    @remove="$emit('remove', tag)"
  >
    <q-icon name="link" size="xs" class="q-mr-xs" />
    {{ tag.name }}
  </q-chip>
</template>

<script>
export default {
  name: 'VinculoBadge',
  props: {
    tag: {
      type: Object,
      required: true,
    },
    removable: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['remove'],
}
</script>

<style lang="scss" scoped>
.intelligence-vinculo-badge {
  transition: all 0.2s ease;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  :deep(.q-chip__icon--remove) {
    opacity: 0.7;

    &:hover {
      opacity: 1;
    }
  }
}
</style>
