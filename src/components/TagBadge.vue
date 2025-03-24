<!-- src/components/TagBadge.vue -->
<template>
  <q-chip
    :style="`background-color: ${tag.color}10; color: ${tag.color}; border: 1px solid ${tag.color}50;`"
    dense
    class="intelligence-tag-badge"
    :clickable="clickable"
    @click="handleClick"
    :removable="removable"
    @remove="$emit('remove', tag)"
  >
    <q-icon name="local_offer" size="xs" class="q-mr-xs" />
    {{ tag.name }}
  </q-chip>
</template>

<script>
export default {
  name: 'TagBadge',
  props: {
    tag: {
      type: Object,
      required: true,
    },
    removable: {
      type: Boolean,
      default: false,
    },
    clickable: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['click', 'remove'],
  methods: {
    handleClick() {
      this.$emit('click', this.tag)
    },
  },
}
</script>

<style lang="scss" scoped>
.intelligence-tag-badge {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    filter: brightness(1.1);
  }

  :deep(.q-chip__icon--remove) {
    opacity: 0.7;

    &:hover {
      opacity: 1;
    }
  }
}
</style>
