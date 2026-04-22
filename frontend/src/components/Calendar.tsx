import { useState, useEffect, useMemo } from 'react';
import {
    DndContext,
    PointerSensor,
    TouchSensor,
    closestCenter,
    useSensor,
    useSensors,
    type DragEndEvent,
} from '@dnd-kit/core';
import {
    SortableContext,
    arrayMove,
    useSortable,
    verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { calendarService } from '../services/calendarService';
import type { CalendarInfo, CalendarType, CalendarEvent } from '../services/calendarService';
import { useAuth } from '../context/AuthContext';
import '../styles/Calendar.css';

const TASK_ORDER_STORAGE_KEY = 'my_calendar_task_order_v1';

interface SortableTaskItemProps {
    event: CalendarEvent;
    savingTask: boolean;
    deletingTaskId: number | null;
    onEditTask: (event: CalendarEvent) => void;
    onDeleteTask: (eventId?: number) => void;
}

const SortableTaskItem = ({ event, savingTask, deletingTaskId, onEditTask, onDeleteTask }: SortableTaskItemProps) => {
    const eventId = event.id;

    if (!eventId) {
        return null;
    }

    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: eventId });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={`my-calendar-task-item ${isDragging ? 'dragging' : ''}`}
        >
            <button
                type="button"
                className="my-calendar-drag-handle"
                aria-label="Görevi taşımak için basılı tut ve sürükle"
                {...attributes}
                {...listeners}
            >
                ⋮⋮
            </button>
            <div className="my-calendar-task-content">
                <p className="my-calendar-task-title">{event.title}</p>
                <p className="my-calendar-task-desc">{event.description || 'Açıklama yok'}</p>
            </div>
            <div className="my-calendar-task-actions">
                <button
                    type="button"
                    className="my-calendar-task-edit"
                    onClick={() => onEditTask(event)}
                    disabled={savingTask || deletingTaskId === event.id}
                >
                    Düzenle
                </button>
                <button
                    type="button"
                    className="my-calendar-task-delete"
                    onClick={() => onDeleteTask(event.id)}
                    disabled={savingTask || deletingTaskId === event.id}
                >
                    {deletingTaskId === event.id ? 'Siliniyor...' : 'Sil'}
                </button>
            </div>
        </div>
    );
};

export const Calendar = ({ isOpen: propIsOpen, onToggle, openMyCalendarToken }: { isOpen?: boolean; onToggle?: () => void; openMyCalendarToken?: number } = {}) => {
    const { user } = useAuth();

    // State
    const [academicCalendar, setAcademicCalendar] = useState<CalendarInfo | null>(null);
    const [myCalendar, setMyCalendar] = useState<CalendarInfo | null>(null);
    const [mainTypes, setMainTypes] = useState<CalendarType[]>([]);
    const [subTypes, setSubTypes] = useState<{ [key: string]: CalendarType[] }>({});
    const [calendarMode, setCalendarMode] = useState<'academic' | 'my'>('my');

    // Selections
    const [selectedMain, setSelectedMain] = useState('general');
    const [selectedSub, setSelectedSub] = useState('');

    // Calendar Grid State
    const [currentDate, setCurrentDate] = useState(new Date());
    const [loadingAcademic, setLoadingAcademic] = useState(true);
    const [loadingMyCalendar, setLoadingMyCalendar] = useState(false);
    const [myCalendarError, setMyCalendarError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);

    // My calendar task form
    const [selectedDay, setSelectedDay] = useState<number | null>(null);
    const [taskTitle, setTaskTitle] = useState('');
    const [taskDescription, setTaskDescription] = useState('');
    const [savingTask, setSavingTask] = useState(false);
    const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
    const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);
    const [taskOrderMap, setTaskOrderMap] = useState<Record<string, number[]>>({});

    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));

    // Initial Load
    useEffect(() => {
        try {
            const savedOrder = localStorage.getItem(TASK_ORDER_STORAGE_KEY);
            if (!savedOrder) {
                return;
            }

            const parsed = JSON.parse(savedOrder) as Record<string, number[]>;
            setTaskOrderMap(parsed);
        } catch {
            localStorage.removeItem(TASK_ORDER_STORAGE_KEY);
        }
    }, []);

    useEffect(() => {
        const loadTypes = async () => {
            try {
                const data = await calendarService.getTypes();
                setMainTypes(data.calendars);
                setSubTypes(data.sub_calendars);
            } catch (err) {
                console.error("Takvim tipleri yüklenemedi", err);
            }
        };
        loadTypes();
    }, []);

    // Fetch Events when selection changes
    useEffect(() => {
        const fetchData = async () => {
            setLoadingAcademic(true);
            try {
                // Eğer alt kategori seçildiyse onu, yoksa ana kategoriyi kullan
                const idToFetch = selectedSub || selectedMain;
                const data = await calendarService.getEvents(idToFetch);
                setAcademicCalendar(data);
            } catch (err) {
                console.error("Takvim verisi yüklenemedi", err);
            } finally {
                setLoadingAcademic(false);
            }
        };

        // Alt kategori gerektirmeyen veya alt kategorisi seçilmiş tipler için fetch et
        const mainType = mainTypes.find(t => t.id === selectedMain);
        if (mainType) {
            if (!mainType.has_sub || (mainType.has_sub && selectedSub)) {
                fetchData();
            }
        }
    }, [selectedMain, selectedSub, mainTypes]);

    useEffect(() => {
        const loadMyCalendar = async () => {
            if (!user || calendarMode !== 'my') {
                return;
            }

            setLoadingMyCalendar(true);
            setMyCalendarError(null);

            try {
                const data = await calendarService.getMyEvents();
                setMyCalendar(data);
            } catch (err) {
                const message = err instanceof Error ? err.message : 'Benim takvimim yüklenemedi';
                setMyCalendarError(message);
            } finally {
                setLoadingMyCalendar(false);
            }
        };

        void loadMyCalendar();
    }, [calendarMode, user]);

    useEffect(() => {
        // Navbar'daki Takvim butonundan her gelişte Benim Takvimim'i aç.
        setCalendarMode('my');
    }, [openMyCalendarToken]);

    useEffect(() => {
        // Sekme değişince görev formunu sıfırla
        setSelectedDay(null);
        setTaskTitle('');
        setTaskDescription('');
        setEditingTaskId(null);
    }, [calendarMode, currentDate]);

    // Main type değişince sub type'ı sıfırla ve gerekirse otomatik ilkini seç
    useEffect(() => {
        const mainType = mainTypes.find(t => t.id === selectedMain);
        if (mainType?.has_sub) {
            const subs = subTypes[selectedMain];
            if (subs && subs.length > 0) {
                setSelectedSub(subs[0].id); // Otomatik ilkini seç
            } else {
                setSelectedSub('');
            }
        } else {
            setSelectedSub('');
        }
    }, [selectedMain, mainTypes, subTypes]);


    // Calendar Logic
    const getDaysInMonth = (date: Date) => {
        return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (date: Date) => {
        // 0 = Sunday, 1 = Monday. We want Monday start (0=Mon, 6=Sun)
        let day = new Date(date.getFullYear(), date.getMonth(), 1).getDay();
        return day === 0 ? 6 : day - 1;
    };

    const changeMonth = (offset: number) => {
        const newDate = new Date(currentDate);
        newDate.setMonth(newDate.getMonth() + offset);
        setCurrentDate(newDate);
    };

    const formatDateForSave = (day: number) => {
        const year = currentDate.getFullYear();
        const month = `${currentDate.getMonth() + 1}`.padStart(2, '0');
        const formattedDay = `${day}`.padStart(2, '0');
        return `${year}-${month}-${formattedDay}`;
    };

    const formatDateForDisplay = (day: number) => {
        const monthNames = ['ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik'];
        const year = currentDate.getFullYear();
        const month = monthNames[currentDate.getMonth()];
        return `${day} ${month} ${year}`;
    };

    // Etkinlikleri günlere dağıt
    const getEventsForDay = (events: CalendarInfo['events'], day: number) => {
        if (!events) return [];

        const currentMonthStr = currentDate.toISOString().slice(0, 7); // YYYY-MM
        const dayStr = day < 10 ? `0${day}` : `${day}`;
        const targetDate = `${currentMonthStr}-${dayStr}`;

        return events.filter(event => {
            // Basit string karşılaştırması (YYY-MM-DD)
            return targetDate >= event.start && targetDate <= event.end;
        });
    };

    const handleDayClick = (day: number, isEmpty: boolean) => {
        if (isEmpty || calendarMode !== 'my' || !user) {
            return;
        }
        setSelectedDay(day);
        setTaskTitle('');
        setTaskDescription('');
        setEditingTaskId(null);
    };

    const handleSaveTask = async () => {
        if (!selectedDay || !taskTitle.trim()) {
            return;
        }

        setSavingTask(true);
        try {
            if (editingTaskId) {
                await calendarService.updateMyEvent(editingTaskId, {
                    date: formatDateForSave(selectedDay),
                    title: taskTitle.trim(),
                    description: taskDescription.trim() || undefined,
                });
            } else {
                await calendarService.createMyEvent({
                    date: formatDateForSave(selectedDay),
                    title: taskTitle.trim(),
                    description: taskDescription.trim() || undefined,
                });
            }

            const data = await calendarService.getMyEvents();
            setMyCalendar(data);
            setTaskTitle('');
            setTaskDescription('');
            setEditingTaskId(null);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Yapılıcak kaydedilemedi';
            setMyCalendarError(message);
        } finally {
            setSavingTask(false);
        }
    };

    const handleEditTask = (event: CalendarEvent) => {
        if (!event.id) {
            return;
        }

        const eventDate = new Date(`${event.start}T00:00:00`);
        if (
            eventDate.getFullYear() === currentDate.getFullYear()
            && eventDate.getMonth() === currentDate.getMonth()
        ) {
            setSelectedDay(eventDate.getDate());
        }

        setTaskTitle(event.title);
        setTaskDescription(event.description || '');
        setEditingTaskId(event.id);
    };

    const handleDeleteTask = async (eventId?: number) => {
        if (!eventId) {
            return;
        }

        setDeletingTaskId(eventId);
        try {
            await calendarService.deleteMyEvent(eventId);
            const data = await calendarService.getMyEvents();
            setMyCalendar(data);

            if (editingTaskId === eventId) {
                setEditingTaskId(null);
                setTaskTitle('');
                setTaskDescription('');
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Görev silinemedi';
            setMyCalendarError(message);
        } finally {
            setDeletingTaskId(null);
        }
    };

    const renderCalendarGrid = (eventsSource: CalendarInfo['events']) => {
        const daysInMonth = getDaysInMonth(currentDate);
        const firstDay = getFirstDayOfMonth(currentDate);
        const days = [];

        // Empty cells for previous month
        for (let i = 0; i < firstDay; i++) {
            days.push(<div key={`empty-${i}`} className="day-cell empty"></div>);
        }

        // Days
        const today = new Date();
        const isCurrentMonth = today.getMonth() === currentDate.getMonth() && today.getFullYear() === currentDate.getFullYear();

        for (let day = 1; day <= daysInMonth; day++) {
            const events = getEventsForDay(eventsSource, day);
            const isToday = isCurrentMonth && day === today.getDate();
            const isSelected = calendarMode === 'my' && selectedDay === day;

            days.push(
                <div
                    key={day}
                    className={`day-cell ${isToday ? 'today' : ''} ${events.length > 0 ? 'has-events' : ''} ${isSelected ? 'selected' : ''} ${calendarMode === 'my' ? 'clickable' : ''}`}
                    onClick={() => handleDayClick(day, false)}
                >
                    <span className="day-number">{day}</span>
                    <div className="day-events">
                        {events.map((event, idx) => (
                            <div
                                key={idx}
                                className={`event-bar event-type-${event.type}`}
                                title={`${event.title} (${event.start_formatted} - ${event.end_formatted})`}
                            >
                                {event.title}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        return days;
    };

    const months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
    const daysOfWeek = ["Pts", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
    const activeCalendar = calendarMode === 'academic' ? academicCalendar : myCalendar;
    const isLoading = calendarMode === 'academic' ? loadingAcademic : loadingMyCalendar;
    const selectedMainName = mainTypes.find(t => t.id === selectedMain)?.name || 'Akademik Takvim';
    const selectedDayEvents = selectedDay && calendarMode === 'my'
        ? getEventsForDay(myCalendar?.events || [], selectedDay)
        : [];

    const selectedDayTaskIds = useMemo(() => (
        selectedDayEvents
            .map((event) => event.id)
            .filter((id): id is number => typeof id === 'number')
    ), [selectedDayEvents]);

    const persistTaskOrder = (nextOrderMap: Record<string, number[]>) => {
        localStorage.setItem(TASK_ORDER_STORAGE_KEY, JSON.stringify(nextOrderMap));
    };

    useEffect(() => {
        if (!selectedDay || selectedDayTaskIds.length === 0) {
            return;
        }

        const dateKey = formatDateForSave(selectedDay);

        setTaskOrderMap((prev) => {
            const existingOrder = prev[dateKey] || [];
            const normalizedOrder = [
                ...existingOrder.filter((id) => selectedDayTaskIds.includes(id)),
                ...selectedDayTaskIds.filter((id) => !existingOrder.includes(id)),
            ];

            if (
                existingOrder.length === normalizedOrder.length
                && existingOrder.every((id, idx) => id === normalizedOrder[idx])
            ) {
                return prev;
            }

            const next = {
                ...prev,
                [dateKey]: normalizedOrder,
            };

            persistTaskOrder(next);
            return next;
        });
    }, [selectedDay, selectedDayTaskIds]);

    const orderedSelectedDayEvents = useMemo(() => {
        if (!selectedDay || selectedDayEvents.length <= 1) {
            return selectedDayEvents;
        }

        const dateKey = formatDateForSave(selectedDay);
        const orderForDate = taskOrderMap[dateKey] || [];

        if (orderForDate.length === 0) {
            return selectedDayEvents;
        }

        const orderIndexMap = new Map(orderForDate.map((id, index) => [id, index]));

        return [...selectedDayEvents].sort((a, b) => {
            const aId = a.id ?? Number.MAX_SAFE_INTEGER;
            const bId = b.id ?? Number.MAX_SAFE_INTEGER;
            const aOrder = orderIndexMap.get(aId) ?? Number.MAX_SAFE_INTEGER;
            const bOrder = orderIndexMap.get(bId) ?? Number.MAX_SAFE_INTEGER;

            if (aOrder !== bOrder) {
                return aOrder - bOrder;
            }

            return aId - bId;
        });
    }, [selectedDay, selectedDayEvents, taskOrderMap]);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 6,
            },
        }),
        useSensor(TouchSensor, {
            activationConstraint: {
                delay: 220,
                tolerance: 8,
            },
        }),
    );

    const handleTaskDragEnd = (event: DragEndEvent) => {
        if (!selectedDay || !event.over) {
            return;
        }

        const activeId = Number(event.active.id);
        const overId = Number(event.over.id);

        if (Number.isNaN(activeId) || Number.isNaN(overId) || activeId === overId) {
            return;
        }

        const dateKey = formatDateForSave(selectedDay);
        const currentOrder = taskOrderMap[dateKey] || selectedDayTaskIds;
        const oldIndex = currentOrder.indexOf(activeId);
        const newIndex = currentOrder.indexOf(overId);

        if (oldIndex === -1 || newIndex === -1) {
            return;
        }

        const nextOrder = arrayMove(currentOrder, oldIndex, newIndex);

        setTaskOrderMap((prev) => {
            const next = {
                ...prev,
                [dateKey]: nextOrder,
            };

            persistTaskOrder(next);
            return next;
        });
    };

    return (
        <div className="calendar-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>📅 Takvimler</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                <div className="calendar-mode-tabs">
                    <button
                        type="button"
                        className={`calendar-mode-tab ${calendarMode === 'my' ? 'active' : ''}`}
                        onClick={() => setCalendarMode('my')}
                    >
                        Ajandam
                    </button>
                    <button
                        type="button"
                        className={`calendar-mode-tab ${calendarMode === 'academic' ? 'active' : ''}`}
                        onClick={() => setCalendarMode('academic')}
                    >
                        Akademik Takvim
                    </button>
                </div>

                {/* Seçiciler */}
                {calendarMode === 'academic' && (
                    <div className="selectors-container">
                        <div className="selector-group">
                            <label>Birim Seçiniz:</label>
                            <select
                                value={selectedMain}
                                onChange={(e) => setSelectedMain(e.target.value)}
                                className="unit-select"
                                onClick={(e) => e.stopPropagation()}
                            >
                                {mainTypes.map(t => (
                                    <option key={t.id} value={t.id}>{t.name}</option>
                                ))}
                            </select>
                        </div>

                        {/* Alt Seçici (Varsa) */}
                        {mainTypes.find(t => t.id === selectedMain)?.has_sub && (
                            <div className="selector-group">
                                <label>Dönem Seçiniz:</label>
                                <select
                                    value={selectedSub}
                                    onChange={(e) => setSelectedSub(e.target.value)}
                                    className="unit-select"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    {subTypes[selectedMain]?.map(t => (
                                        <option key={t.id} value={t.id}>{t.name}</option>
                                    ))}
                                </select>
                            </div>
                        )}
                    </div>
                )}

                {calendarMode === 'my' && !user && (
                    <div className="calendar-locked-state" role="note" aria-label="Ajandam kilitli">
                        <p>Ajandam hizmetini kullanabilmek için giriş yapın.</p>
                    </div>
                )}

                {isLoading ? (
                    <div className="loading">Yükleniyor...</div>
                ) : calendarMode === 'my' && !user ? null : (
                    <div className="calendar-grid-view">
                        <p className="calendar-view-title">
                            {calendarMode === 'academic' ? selectedMainName : 'Ajandam'}
                        </p>

                        {/* Navigasyon */}
                        <div className="calendar-nav">
                            <button onClick={() => changeMonth(-1)}>❮</button>
                            <span className="current-month">
                                {months[currentDate.getMonth()]} {currentDate.getFullYear()}
                            </span>
                            <button onClick={() => changeMonth(1)}>❯</button>
                        </div>

                        {/* Gün İsimleri */}
                        <div className="days-header">
                            {daysOfWeek.map(d => <span key={d}>{d}</span>)}
                        </div>

                        {/* Günler Grid */}
                        <div className="days-grid">
                            {renderCalendarGrid(activeCalendar?.events || [])}
                        </div>

                        {calendarMode === 'my' && selectedDay && (
                            <>
                                <div className="my-calendar-tasks">
                                    <h4>{formatDateForDisplay(selectedDay)} yapılacaklar</h4>
                                    {selectedDayEvents.length > 0 ? (
                                        <DndContext
                                            sensors={sensors}
                                            collisionDetection={closestCenter}
                                            onDragEnd={handleTaskDragEnd}
                                        >
                                            <SortableContext
                                                items={orderedSelectedDayEvents
                                                    .map((event) => event.id)
                                                    .filter((id): id is number => typeof id === 'number')}
                                                strategy={verticalListSortingStrategy}
                                            >
                                                <div className="my-calendar-task-list">
                                                    {orderedSelectedDayEvents.map((event) => (
                                                        <SortableTaskItem
                                                            key={event.id || `${event.title}-${event.start}`}
                                                            event={event}
                                                            savingTask={savingTask}
                                                            deletingTaskId={deletingTaskId}
                                                            onEditTask={handleEditTask}
                                                            onDeleteTask={(eventId) => void handleDeleteTask(eventId)}
                                                        />
                                                    ))}
                                                </div>
                                            </SortableContext>
                                        </DndContext>
                                    ) : (
                                        <p className="my-calendar-empty">Bu gün için henüz yapılacaklar yok.</p>
                                    )}
                                </div>

                                <div className="my-calendar-form">
                                    <h4>
                                        {editingTaskId
                                            ? `${formatDateForDisplay(selectedDay)} görevi düzenle`
                                            : `${formatDateForDisplay(selectedDay)} için yapılacaklar`}
                                    </h4>
                                    <input
                                        type="text"
                                        placeholder="Başlık"
                                        value={taskTitle}
                                        onChange={(e) => setTaskTitle(e.target.value)}
                                    />
                                    <textarea
                                        placeholder="Açıklama (opsiyonel)"
                                        value={taskDescription}
                                        onChange={(e) => setTaskDescription(e.target.value)}
                                        rows={3}
                                    />
                                    <div className="my-calendar-form-actions">
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setSelectedDay(null);
                                                setEditingTaskId(null);
                                                setTaskTitle('');
                                                setTaskDescription('');
                                            }}
                                        >
                                            Vazgeç
                                        </button>
                                        <button type="button" onClick={handleSaveTask} disabled={savingTask || !taskTitle.trim()}>
                                            {savingTask ? (editingTaskId ? 'Güncelleniyor...' : 'Kaydediliyor...') : (editingTaskId ? 'Güncelle' : 'Kaydet')}
                                        </button>
                                    </div>
                                </div>
                            </>
                        )}

                        {myCalendarError && calendarMode === 'my' && (
                            <p className="calendar-error">{myCalendarError}</p>
                        )}

                        {/* Legend */}
                        {calendarMode === 'academic' && (
                            <div className="calendar-legend">
                                <>
                                    <div className="legend-item">
                                        <span className="legend-color event-type-registration"></span> Kayıt/Seçim
                                    </div>
                                    <div className="legend-item">
                                        <span className="legend-color event-type-term"></span> Ders Dönemi
                                    </div>
                                    <div className="legend-item">
                                        <span className="legend-color event-type-exam"></span> Sınav
                                    </div>
                                    <div className="legend-item">
                                        <span className="legend-color event-type-holiday"></span> Tatil
                                    </div>
                                </>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
