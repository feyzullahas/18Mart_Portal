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

    async getKykMeals(): Promise<Meal[]> {
        const response = await fetch(`${API_BASE_URL}/meals/kyk`);
        if (!response.ok) throw new Error('KYK yemekleri alınamadı');
        return response.json();
    }
};
