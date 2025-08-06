"use client";

import { MainContent } from "@/components/layout/MainContent";

interface ContactDetailPageProps {
  params: {
    contactId: string;
  };
}

export default function ContactDetailPage({ params }: ContactDetailPageProps) {
  return (
    <MainContent
      mode="contacts"
      selectedItem={params.contactId}
      onItemSelect={() => {}}
    />
  );
}