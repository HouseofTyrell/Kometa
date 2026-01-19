<script setup lang="ts">
import { ref } from 'vue';
import { Card, Button, Badge, Modal } from '@/components/common';

const emit = defineEmits<{
  (e: 'select', template: CollectionTemplate): void;
}>();

interface CollectionTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  yaml: string;
  tags: string[];
}

const selectedTemplate = ref<CollectionTemplate | null>(null);
const showPreview = ref(false);

const templates: CollectionTemplate[] = [
  // Trending & Popular
  {
    id: 'tmdb-trending',
    name: 'Trending Movies',
    description: 'Movies trending on TMDb this week',
    category: 'Trending',
    icon: '&#128293;',
    tags: ['TMDb', 'Movies', 'Popular'],
    yaml: `collections:
  Trending Movies:
    tmdb_trending_weekly: 20
    collection_order: custom
    sync_mode: sync
    sort_title: "!001_Trending"
    summary: "Movies trending this week on TMDb"
`,
  },
  {
    id: 'tmdb-popular',
    name: 'Popular Movies',
    description: 'Most popular movies on TMDb',
    category: 'Trending',
    icon: '&#11088;',
    tags: ['TMDb', 'Movies', 'Popular'],
    yaml: `collections:
  Popular Movies:
    tmdb_popular: 40
    collection_order: custom
    sync_mode: sync
    sort_title: "!002_Popular"
    summary: "The most popular movies on TMDb"
`,
  },
  {
    id: 'tmdb-top-rated',
    name: 'Top Rated Movies',
    description: 'Highest rated movies on TMDb',
    category: 'Trending',
    icon: '&#127942;',
    tags: ['TMDb', 'Movies', 'Ratings'],
    yaml: `collections:
  Top Rated:
    tmdb_top_rated: 100
    collection_order: custom
    sync_mode: sync
    sort_title: "!003_TopRated"
    summary: "The highest rated movies on TMDb"
`,
  },
  // Award Collections
  {
    id: 'oscar-winners',
    name: 'Oscar Best Picture',
    description: 'Academy Award Best Picture winners',
    category: 'Awards',
    icon: '&#127941;',
    tags: ['IMDb', 'Awards', 'Movies'],
    yaml: `collections:
  Oscar Best Picture:
    imdb_list: https://www.imdb.com/search/title/?groups=oscar_best_picture_winners
    collection_order: release.desc
    sync_mode: sync
    summary: "Academy Award for Best Picture winners"
`,
  },
  {
    id: 'imdb-top-250',
    name: 'IMDb Top 250',
    description: 'IMDb Top 250 rated movies',
    category: 'Awards',
    icon: '&#127919;',
    tags: ['IMDb', 'Ratings', 'Movies'],
    yaml: `collections:
  IMDb Top 250:
    imdb_chart: top_movies
    collection_order: custom
    sync_mode: sync
    summary: "The top 250 movies as rated by IMDb users"
`,
  },
  // Genre Collections
  {
    id: 'genre-action',
    name: 'Action Movies',
    description: 'Popular action movies',
    category: 'Genres',
    icon: '&#128165;',
    tags: ['TMDb', 'Genre', 'Movies'],
    yaml: `collections:
  Action:
    tmdb_discover:
      with_genres: 28
      sort_by: popularity.desc
      limit: 100
    collection_order: custom
    sync_mode: sync
    summary: "Popular action movies"
`,
  },
  {
    id: 'genre-comedy',
    name: 'Comedy Movies',
    description: 'Popular comedy movies',
    category: 'Genres',
    icon: '&#128514;',
    tags: ['TMDb', 'Genre', 'Movies'],
    yaml: `collections:
  Comedy:
    tmdb_discover:
      with_genres: 35
      sort_by: popularity.desc
      limit: 100
    collection_order: custom
    sync_mode: sync
    summary: "Popular comedy movies"
`,
  },
  {
    id: 'genre-horror',
    name: 'Horror Movies',
    description: 'Popular horror movies',
    category: 'Genres',
    icon: '&#128123;',
    tags: ['TMDb', 'Genre', 'Movies'],
    yaml: `collections:
  Horror:
    tmdb_discover:
      with_genres: 27
      sort_by: popularity.desc
      limit: 100
    collection_order: custom
    sync_mode: sync
    summary: "Popular horror movies"
`,
  },
  // Decade Collections
  {
    id: 'decade-2020s',
    name: '2020s Movies',
    description: 'Movies from the 2020s',
    category: 'Decades',
    icon: '&#128197;',
    tags: ['TMDb', 'Decade', 'Movies'],
    yaml: `collections:
  2020s Movies:
    tmdb_discover:
      primary_release_date.gte: 2020-01-01
      sort_by: popularity.desc
      limit: 100
    collection_order: release.desc
    sync_mode: sync
    summary: "Popular movies from the 2020s"
`,
  },
  {
    id: 'decade-80s',
    name: '80s Classics',
    description: 'Classic movies from the 1980s',
    category: 'Decades',
    icon: '&#127926;',
    tags: ['TMDb', 'Decade', 'Movies'],
    yaml: `collections:
  80s Classics:
    tmdb_discover:
      primary_release_date.gte: 1980-01-01
      primary_release_date.lte: 1989-12-31
      vote_count.gte: 1000
      sort_by: vote_average.desc
      limit: 100
    collection_order: release
    sync_mode: sync
    summary: "Classic movies from the 1980s"
`,
  },
  // Studio Collections
  {
    id: 'studio-pixar',
    name: 'Pixar Collection',
    description: 'All Pixar animated movies',
    category: 'Studios',
    icon: '&#127916;',
    tags: ['TMDb', 'Studio', 'Animation'],
    yaml: `collections:
  Pixar:
    tmdb_company: 3
    collection_order: release
    sync_mode: sync
    summary: "Pixar Animation Studios movies"
`,
  },
  {
    id: 'studio-marvel',
    name: 'Marvel Cinematic Universe',
    description: 'MCU movies in timeline order',
    category: 'Studios',
    icon: '&#129464;',
    tags: ['TMDb', 'Studio', 'Superhero'],
    yaml: `collections:
  Marvel Cinematic Universe:
    tmdb_list: 131292
    collection_order: custom
    sync_mode: sync
    summary: "The Marvel Cinematic Universe in timeline order"
`,
  },
  // TV Shows
  {
    id: 'tv-trending',
    name: 'Trending TV Shows',
    description: 'TV shows trending this week',
    category: 'TV Shows',
    icon: '&#128250;',
    tags: ['TMDb', 'TV', 'Trending'],
    yaml: `collections:
  Trending Shows:
    tmdb_trending_weekly: 20
    collection_order: custom
    sync_mode: sync
    summary: "TV shows trending this week"
`,
  },
  {
    id: 'tv-top-rated',
    name: 'Top Rated Shows',
    description: 'Highest rated TV shows',
    category: 'TV Shows',
    icon: '&#127942;',
    tags: ['TMDb', 'TV', 'Ratings'],
    yaml: `collections:
  Top Rated Shows:
    tmdb_top_rated: 50
    collection_order: custom
    sync_mode: sync
    summary: "The highest rated TV shows"
`,
  },
];

const categories = [...new Set(templates.map((t) => t.category))];

function selectTemplate(template: CollectionTemplate) {
  selectedTemplate.value = template;
  showPreview.value = true;
}

function confirmTemplate() {
  if (selectedTemplate.value) {
    emit('select', selectedTemplate.value);
    showPreview.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h3 class="text-lg font-semibold mb-1">Collection Templates</h3>
      <p class="text-sm text-content-secondary">
        Quick-start templates for popular collection types. Click to preview and add to your library.
      </p>
    </div>

    <div
      v-for="category in categories"
      :key="category"
      class="space-y-3"
    >
      <h4 class="font-medium text-sm text-content-secondary uppercase tracking-wide">
        {{ category }}
      </h4>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <button
          v-for="template in templates.filter((t) => t.category === category)"
          :key="template.id"
          class="flex items-start gap-3 p-4 rounded-lg bg-surface-tertiary hover:bg-surface-hover
                 border border-transparent hover:border-kometa-gold/30 transition-all text-left group"
          @click="selectTemplate(template)"
        >
          <span class="text-2xl flex-shrink-0" v-html="template.icon" />
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm group-hover:text-kometa-gold transition-colors">
              {{ template.name }}
            </div>
            <p class="text-xs text-content-secondary mt-0.5 line-clamp-2">
              {{ template.description }}
            </p>
            <div class="flex flex-wrap gap-1 mt-2">
              <Badge
                v-for="tag in template.tags.slice(0, 2)"
                :key="tag"
                variant="default"
                size="sm"
              >
                {{ tag }}
              </Badge>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Preview Modal -->
    <Modal
      v-model:open="showPreview"
      :title="selectedTemplate?.name || 'Template Preview'"
      size="lg"
    >
      <div
        v-if="selectedTemplate"
        class="space-y-4"
      >
        <p class="text-content-secondary">
          {{ selectedTemplate.description }}
        </p>

        <div class="flex flex-wrap gap-2">
          <Badge
            v-for="tag in selectedTemplate.tags"
            :key="tag"
            variant="default"
          >
            {{ tag }}
          </Badge>
        </div>

        <div>
          <h4 class="font-medium text-sm mb-2">YAML Configuration</h4>
          <pre class="p-4 rounded-lg bg-surface-tertiary text-sm font-mono overflow-auto max-h-64">{{ selectedTemplate.yaml }}</pre>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-border">
          <Button
            variant="secondary"
            @click="showPreview = false"
          >
            Cancel
          </Button>
          <Button @click="confirmTemplate">
            Add to Library
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>
