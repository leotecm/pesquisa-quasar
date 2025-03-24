<!-- src/pages/UploadDocument.vue -->
<template>
  <q-page padding>
    <h4 class="q-mb-lg">Adicionar Novo Documento</h4>

    <q-card class="q-pa-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Selecione um arquivo para upload</div>

        <q-file
          v-model="file"
          label="Selecionar Documento"
          filled
          bottom-slots
          counter
          accept=".doc,.docx,.pdf,.txt"
          @update:model-value="onFileSelected"
        >
          <template v-slot:prepend>
            <q-icon name="attach_file" />
          </template>
          <template v-slot:hint> Formatos suportados: .doc, .docx, .pdf, .txt </template>
        </q-file>

        <div class="q-mt-md" v-if="file">
          <q-chip>
            <q-avatar
              :icon="getFileIcon(file.name)"
              :color="getFileColor(file.name)"
              text-color="white"
            />
            {{ file.name }}
          </q-chip>
        </div>

        <q-banner v-if="uploadNotAvailable" class="bg-amber-2 q-mt-md">
          <template v-slot:avatar>
            <q-icon name="warning" color="amber" />
          </template>
          O upload de arquivos não está disponível no backend atual. Para implementar, seria
          necessário adicionar um endpoint de upload no servidor Python.
        </q-banner>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn label="Cancelar" color="grey" to="/" flat :disable="uploading" />
        <q-btn
          label="Salvar Documento"
          color="primary"
          :loading="uploading"
          :disable="!file || uploadNotAvailable"
          @click="uploadDocument"
        />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { saveDocument } from 'src/services/fileService'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

export default {
  name: 'UploadDocument',
  setup() {
    const file = ref(null)
    const uploading = ref(false)
    const uploadNotAvailable = ref(true) // Definido como true pois o backend não suporta upload
    const router = useRouter()
    const $q = useQuasar()

    function getFileExtension(filename) {
      return filename.split('.').pop().toLowerCase()
    }

    function getFileIcon(filename) {
      const ext = getFileExtension(filename)
      const icons = {
        doc: 'mdi-file-word',
        docx: 'mdi-file-word',
        pdf: 'mdi-file-pdf',
        txt: 'mdi-file-document',
      }
      return icons[ext] || 'insert_drive_file'
    }

    function getFileColor(filename) {
      const ext = getFileExtension(filename)
      const colors = {
        doc: 'blue',
        docx: 'blue',
        pdf: 'red',
        txt: 'grey-7',
      }
      return colors[ext] || 'grey'
    }

    function onFileSelected() {
      // Validação adicional se necessário
      console.log('Arquivo selecionado:', file.value)
    }

    async function uploadDocument() {
      if (!file.value || uploadNotAvailable.value) return

      uploading.value = true
      try {
        // Observe que não passamos mais o arquivo para saveDocument()
        await saveDocument()
        $q.notify({
          color: 'positive',
          message: 'Documento salvo com sucesso!',
          icon: 'check',
        })
        router.push('/')
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: `Erro ao salvar documento: ${error.message}`,
          icon: 'error',
        })
        console.error(error)
      } finally {
        uploading.value = false
      }
    }

    return {
      file,
      uploading,
      uploadNotAvailable,
      onFileSelected,
      uploadDocument,
      getFileIcon,
      getFileColor,
    }
  },
}
</script>
