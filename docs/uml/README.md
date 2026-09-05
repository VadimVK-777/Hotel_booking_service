# UML-диаграммы

В каталоге находятся PlantUML-исходники всех основных типов UML.

Структурные диаграммы:

- [`component-diagram.puml`](component-diagram.puml) — компоненты приложения и зависимости;
- [`class-diagram.puml`](class-diagram.puml) — модели предметной области и классы слоёв;
- [`object-diagram.puml`](object-diagram.puml) — пример экземпляров номеров и броней;
- [`package-diagram.puml`](package-diagram.puml) — пакеты и зависимости модулей;
- [`composite-structure-diagram.puml`](composite-structure-diagram.puml) — внутренняя структура HTTP-компонента;
- [`deployment-diagram.puml`](deployment-diagram.puml) — контейнеры Docker и PostgreSQL;
- [`profile-diagram.puml`](profile-diagram.puml) — профиль стереотипов архитектуры.

Поведенческие диаграммы:

- [`use-case-diagram.puml`](use-case-diagram.puml) — варианты использования API;
- [`booking-sequence.puml`](booking-sequence.puml) — последовательность создания брони;
- [`activity-diagram.puml`](activity-diagram.puml) — алгоритм создания брони;
- [`state-diagram.puml`](state-diagram.puml) — состояния брони;
- [`communication-diagram.puml`](communication-diagram.puml) — обмен сообщениями компонентов;
- [`interaction-overview.puml`](interaction-overview.puml) — обзор обработки HTTP-запроса;
- [`timing-diagram.puml`](timing-diagram.puml) — временная шкала конкурентного бронирования.

Для генерации PNG или SVG установите PlantUML и выполните:

```bash
plantuml docs/uml/*.puml
```
