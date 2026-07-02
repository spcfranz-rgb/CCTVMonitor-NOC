/*
 * Copyright (c) 2026 Timothy Franz. All Rights Reserved.
 *
 * This file is part of Project Lighthouse.
 * Unauthorized copying of this file, via any medium, is strictly prohibited.
 * Proprietary and confidential.
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

const app = createApp(App)
app.use(createPinia())
app.use(router)

app.mount('#app')
