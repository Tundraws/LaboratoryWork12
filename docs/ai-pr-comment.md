# Доказательство комментария AI PR workflow

В репозитории настроен workflow `.github/workflows/ai-pr-review.yml`. Он запускается на Pull Request, выполняет тесты и публикует комментарий в PR.

Если секрет `OPENAI_API_KEY` не задан, workflow публикует fallback-комментарий такого вида:

```markdown
### AI PR summary

OPENAI_API_KEY is not configured, so this workflow published a deterministic fallback summary.

Changed files: <list of changed files>.

Automated tests were executed before this comment.
```

Если `OPENAI_API_KEY` задан, workflow отправляет diff-stat в OpenAI API и публикует AI summary с кратким описанием изменений, рисков и выполненных тестов.

Скриншот комментария из Pull Request сохранен в `docs/screenshots/ai-pr-comment.jpg`.

CI workflow verification branch.
