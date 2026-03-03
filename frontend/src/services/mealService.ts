const API_BASE_URL = 'http://127.0.0.1:8000';

export interface Meal {
    name: string;
}

export const mealService = {
    async getOsemMeals(): Promise<Meal[]> {
        const response = await fetch(`${API_BASE_URL}/meals/osem`);
        if (!response.ok) throw new Error('ÖSEM yemekleri alınamadı');
        return response.json();
    },

    async getKykMeals(year?: number, month?: number): Promise<Meal[]> {
        const params = new URLSearchParams();
        if (year !== undefined) params.set('year', year.toString());
        if (month !== undefined) params.set('month', month.toString());
        const qs = params.toString();
        const url = `${API_BASE_URL}/meals/kyk${qs ? '?' + qs : ''}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('KYK yemekleri alınamadı');
        return response.json();
    }
};
