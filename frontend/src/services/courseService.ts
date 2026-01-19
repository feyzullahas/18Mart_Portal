const API_BASE_URL = 'http://127.0.0.1:8000';

export interface Course {
    id: number;
    name: string;
    code: string;
    day: string;
    start_time: string;
    end_time: string;
    location?: string;
    instructor?: string;
}

export interface CourseFormData {
    name: string;
    code: string;
    day: string;
    start_time: string;
    end_time: string;
    location?: string;
    instructor?: string;
}

export interface CoursesByDay {
    [key: string]: Course[];
}

export const courseService = {
    async getAllCourses(): Promise<CoursesByDay> {
        const response = await fetch(`${API_BASE_URL}/courses/`);
        if (!response.ok) throw new Error('Ders programı alınamadı');
        return response.json();
    },

    async getCoursesByDay(day: string): Promise<Course[]> {
        const response = await fetch(`${API_BASE_URL}/courses/${day}`);
        if (!response.ok) throw new Error('Günlük dersler alınamadı');
        return response.json();
    },

    async addCourse(courseData: CourseFormData): Promise<Course> {
        const response = await fetch(`${API_BASE_URL}/courses/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(courseData),
        });
        if (!response.ok) throw new Error('Ders eklenemedi');
        return response.json();
    },

    async updateCourse(courseId: number, courseData: Partial<CourseFormData>): Promise<Course> {
        const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(courseData),
        });
        if (!response.ok) throw new Error('Ders güncellenemedi');
        return response.json();
    },

    async deleteCourse(courseId: number): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Ders silinemedi');
    }
};