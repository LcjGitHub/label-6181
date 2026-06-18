import axios from 'axios'
import type { Manufacturer, ManufacturerForm } from '@/types/manufacturer'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export async function fetchManufacturers(
  country: string = '',
): Promise<Manufacturer[]> {
  const { data } = await http.get<Manufacturer[]>('/manufacturers', {
    params: { country },
  })
  return data
}

export async function fetchManufacturer(id: number): Promise<Manufacturer> {
  const { data } = await http.get<Manufacturer>(`/manufacturers/${id}`)
  return data
}

export async function createManufacturer(
  payload: ManufacturerForm,
): Promise<Manufacturer> {
  const { data } = await http.post<Manufacturer>('/manufacturers', payload)
  return data
}

export async function updateManufacturer(
  id: number,
  payload: ManufacturerForm,
): Promise<Manufacturer> {
  const { data } = await http.put<Manufacturer>(`/manufacturers/${id}`, payload)
  return data
}

export async function deleteManufacturer(id: number): Promise<void> {
  await http.delete(`/manufacturers/${id}`)
}

export async function batchDeleteManufacturers(ids: number[]): Promise<void> {
  await http.post('/manufacturers/batch-delete', { ids })
}
